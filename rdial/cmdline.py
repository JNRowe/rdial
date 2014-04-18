#
# coding=utf-8
"""cmdline - Command line functionality for rdial"""
# Copyright © 2011-2014  James Rowe <jnrowe@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# pylint: disable-msg=C0121

import argparse
import os
import shlex
import subprocess

import aaargh
import arrow
import prettytable

from .events import (Events, TaskRunningError)
from .i18n import (_, N_)
from . import _version
from . import utils

APP = aaargh.App(
    description=_('Simple time tracking for simple people'),
    epilog=_('Please report bugs to https://github.com/JNRowe/issues')
)


# pylint: disable-msg=R0903
class TaskAction(argparse.Action):

    """Define task name, handling --from-dir option."""

    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.task is True:
            namespace.task = os.path.basename(os.path.abspath(os.curdir))
        else:
            namespace.task = values
# pylint: enable-msg=R0903


def task_name_typecheck(string):
    """Check given task name is valid.

    :param str string: Task name to check
    :rtype: :obj:`str`
    :returns: Task name, if valid
    :raises argparse.ArgparseTypeError: If task name is invalid
    """
    if string.startswith('.') or '/' in string or '\000' in string:
        raise argparse.ArgumentTypeError(_('%r is not a valid task name')
                                         % string)
    return string


# pylint: disable-msg=C0103
task_parser = argparse.ArgumentParser(add_help=False)
names_group = task_parser.add_mutually_exclusive_group()
names_group.add_argument('-x', '--from-dir', action='store_true', dest='task',
                         help=_('use directory name as task'))
names_group.add_argument('task', default='default', nargs='?',
                         action=TaskAction, help=_('task name'),
                         type=task_name_typecheck)

duration_parser = argparse.ArgumentParser(add_help=False)
duration_parser.add_argument('-d', '--duration', default='all',
                             choices=['day', 'week', 'month', 'year', 'all'],
                             help=_('filter events for specified time period'))
# pylint: enable-msg=C0103


def filter_events(directory, task=None, duration=None):
    """Filter events for report processing.

    :param str directory: Directory to read events from
    :param str task: Task name to filter on
    :param str duration: Time window to filter on
    :rtype: :obj:`rdial.events.Events`
    :return: Events matching specified criteria
    """
    events = Events.read(directory)
    if task:
        events = events.for_task(task)
    if not duration == 'all':
        today = arrow.now().date()
        if duration == 'week':
            events = events.for_week(*today.isocalendar()[:2])
        else:
            year, month, day = today.year, today.month, today.day
            if duration == 'month':
                day = None
            elif duration == 'year':
                month = None
                day = None
            events = events.for_date(year, month, day)
    return events


def start_time_typecheck(string):
    """Check given start time is valid.

    :param str string: Timestamps to check
    :rtype: :obj:`str`
    :returns: Timestamp, if valid
    :raises argparse.ArgumentTypeError: If timestamp is invalid
    """
    try:
        utils.parse_datetime(string)
    except arrow.parser.ParserError:
        raise argparse.ArgumentTypeError(_('%r is not a valid ISO-8601 time '
                                           'string') % string)
    return string


@APP.cmd(help=_('check storage consistency'))
def fsck(directory, backup, config):
    """Check storage consistency.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    """
    with Events.context(directory, backup) as events:
        last = events[0]
        for event in events[1:]:
            if not last.start + last.delta <= event.start:
                print(utils.fail(_('Overlap:')))
                print(utils.warn('  %r' % last))
                print('  %r' % event)
            last = event


@APP.cmd(help=_('start task'), parents=[task_parser])
@APP.cmd_arg('-n', '--new', action='store_true', help=_('start a new task'))
@APP.cmd_arg('-t', '--time', metavar='time', default='',
             help=_('set start time'), type=start_time_typecheck)
@utils.write_current
def start(directory, backup, config, task, new, time):
    """Start task.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param arrow.Arrow time: Task start time
    """
    with Events.context(directory, backup) as events:
        events.start(task, new, time)


@APP.cmd(help=_('stop task'))
@APP.cmd_arg('-m', '--message', metavar='message', help=_('closing message'))
@APP.cmd_arg('-F', '--file', metavar='file', type=argparse.FileType(),
             help=_('read closing message from file'))
@APP.cmd_arg('--amend', action='store_true',
             help=_('amend previous stop entry'))
@utils.remove_current
def stop(directory, backup, config, message, file, amend):
    """Stop task.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    :param bool amend: Amend a previously stopped event
    """
    if file:
        message = file.read()
    with Events.context(directory, backup) as events:
        last = events.last()
        if amend and last.running():
            raise TaskRunningError(_("Can't amend running task %s!")
                                   % last.task)
        if amend and not message:
            event = events.last()
            message = event.message
        events.stop(message, force=amend)
    event = events.last()
    print(_('Task %s running for %s') % (event.task,
                                         str(event.delta).split('.')[0]))


@APP.cmd(help=_('switch to another task'), parents=[task_parser])
@APP.cmd_arg('-n', '--new', action='store_true', help=_('start a new task'))
@APP.cmd_arg('-m', '--message', metavar='message',
             help=_('closing message for current task'))
@APP.cmd_arg('-F', '--file', metavar='file', type=argparse.FileType(),
             help=_('read closing message for current task from file'))
@utils.write_current
def switch(directory, backup, config, task, new, message, file):
    """Complete last task and start new one.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    """
    if file:
        message = file.read()
    with Events.context(directory, backup) as events:
        if new or task in events.tasks():
            # This is dirty, but we kick on to Events.start() to save
            # duplication of error handling for task names
            events.stop(message)
        event = events.last()
        events.start(task, new)
    print(_('Task %s running for %s') % (event.task,
                                         str(event.delta).split('.')[0]))


@APP.cmd(help=_('run command with timer'), parents=[task_parser])
@APP.cmd_arg('-n', '--new', action='store_true', help=_('start a new task'))
@APP.cmd_arg('-t', '--time', metavar='time', default='',
             help=_('set start time'), type=start_time_typecheck)
@APP.cmd_arg('-m', '--message', metavar='message', help=_('closing message'))
@APP.cmd_arg('-F', '--file', metavar='file', type=argparse.FileType(),
             help=_('read closing message from file'))
@APP.cmd_arg('-c', '--command', metavar='command', help=_('command to run'))
def run(directory, backup, config, task, new, time, message, file, command):
    """Run timed command.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param arrow.Arrow time: Task start time
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    :param str command: Command to run
    """
    with Events.context(directory, backup) as events:
        if events.running():
            raise TaskRunningError(_('Task %s is already started!'
                                     % events.last().task))

        try:
            p = subprocess.Popen(command, shell=True)
        except OSError as e:
            raise utils.RdialError(e.strerror)

        events.start(task, new, time)
        open('%s/.current' % directory, 'w').write(task)

        p.wait()

        if file:
            message = file.read()
        events.stop(message)
    event = events.last()
    print(_('Task %s running for %s') % (event.task,
                                         str(event.delta).split('.')[0]))
    os.unlink('%s/.current' % directory)


@APP.cmd(help=_('run predefined command with timer'))
@APP.cmd_arg('-t', '--time', metavar='time', default='',
             help=_('set start time'), type=start_time_typecheck)
@APP.cmd_arg('-m', '--message', metavar='message', help=_('closing message'))
@APP.cmd_arg('-F', '--file', metavar='file', type=argparse.FileType(),
             help=_('read closing message from file'))
@APP.cmd_arg('wrapper', default='default', help=_('wrapper name'))
def wrapper(directory, backup, config, time, message, file, wrapper):
    """Run predefined timed command.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj.ConfigObj config: Configuration data
    :param datetime.datetime time: Task start time
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    :param str wrapper: Run wrapper to execute
    """
    if not 'run wrappers' in config:
        raise ValueError(_('No %r section in config') % 'run wrappers')
    try:
        command = config['run wrappers'][wrapper]
    except KeyError:
        raise ValueError(_('No such wrapper %r') % wrapper)
    parser = argparse.ArgumentParser(parents=[task_parser, ])
    parser.add_argument('-c', '--command')
    args = parser.parse_args(shlex.split(command))
    run(directory, backup, config, args.task, False, time, message, file,
        args.command)


# pylint: disable-msg=C0103
output_parser = argparse.ArgumentParser(add_help=False)
output_group = output_parser.add_mutually_exclusive_group()
output_group.add_argument('--html', action='store_true',
                          help=_('produce HTML output'))
output_group.add_argument('--human', action='store_true',
                          help=_('produce human-readable output'))
# pylint: enable-msg=C0103


@APP.cmd(help=_('report time tracking data'),
         parents=[duration_parser, task_parser, output_parser])
@APP.cmd_arg('-s', '--sort', default='task', choices=['task', 'time'],
             help=_('field to sort by'))
@APP.cmd_arg('-r', '--reverse', action='store_true',
             help=_('reverse sort order'))
def report(directory, backup, config, task, duration, sort, reverse, html,
           human):
    """Report time tracking data.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    :param str task: Task name to operate on
    :param str duration: Time window to filter on
    :param str sort: Key to sort events on
    :param bool reverse: Reverse sort order
    :param bool html: Produce HTML output
    :param bool human: Produce human-readble output
    """
    if task == 'default':
        # Lazy way to remove duplicate argument definitions
        task = None
    events = filter_events(directory, task, duration)
    if human:
        print(N_('%d event in query', '%d events in query', len(events))
              % len(events))
        print(_('Duration of events %s') % events.sum())
        print(_('First entry started at %s') % events[0].start)
        print(_('Last entry started at %s') % events[-1].start)
        dates = set(e.start.date() for e in events)
        print(_('Events exist on %d dates') % len(dates))
    else:
        table = prettytable.PrettyTable(['task', 'time'])
        formatter = table.get_html_string if html else table.get_string
        try:
            table.align['task'] = 'l'
        except AttributeError:  # prettytable 0.5 compatibility
            table.set_field_align('task', 'l')
        for task in events.tasks():
            table.add_row([task, events.for_task(task).sum()])

        print(formatter(sortby=sort, reversesort=reverse))
    if events.running() and not html:
        current = events.last()
        print(_("Task `%s' started %s")
              % (current.task, current.start.humanize()))


@APP.cmd(help=_('display running task, if any'))
def running(directory, backup, config):
    """Display running task, if any.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    """
    events = Events.read(directory)
    if events.running():
        current = events.last()
        print(_("Task `%s' started %s") % (current.task,
                                           current.start.humanize()))
    else:
        print(utils.warn(_('No task is running!')))


@APP.cmd(help=_('display last event, if any'))
def last(directory, backup, config):
    """Display last event, if any.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    """
    events = Events.read(directory)
    event = events.last()
    if not events.running():
        print(_('Last task %s, ran for %s') % (event.task, event.delta))
    else:
        print(utils.warn(_('Task %s is still running') % event.task))


@APP.cmd(help=_('generate ledger compatible data file'),
         parents=[duration_parser, task_parser])
@APP.cmd_arg('-r', '--rate', metavar='rate',
             help=_('hourly rate for task output'))
def ledger(directory, backup, config, task, duration, rate):
    """Generate ledger compatible data file.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files
    :param configobj config: Configuration data
    :param str task: Task name to operate on
    :param str duration: Time window to filter on
    :param str rate: Rate to assign hours in report
    """
    if task == 'default':
        # Lazy way to remove duplicate argument definitions
        task = None
    events = filter_events(directory, task, duration)
    if events.running():
        print(_(';; Running event not included in output!'))
    for event in events:
        if not event.delta:
            continue
        end = event.start + event.delta
        # Can't use timedelta.total_seconds() as it was only added in 2.7
        seconds = event.delta.days * 86400 + event.delta.seconds
        hours = seconds / 3600.0
        print('%s-%s' % (event.start.format('YYYY-MM-DD * HH:mm'),
                         end.format('HH:mm')))
        print('    (task:%s)  %.2fh%s'
              % (event.task, hours, ' @ %s' % rate if rate else ''))
    if events.running():
        print(_(';; Running event not included in output!'))


def main():
    """Main script."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config')
    args, remaining = parser.parse_known_args()
    cfg = utils.read_config(parser, args.config)

    if 'color' in cfg['rdial']:
        cfg['rdial']['colour'] = cfg['rdial']['color']
    if not cfg['rdial'].as_bool('colour') or os.getenv('NO_COLOUR') \
            or os.getenv('NO_COLOR'):
        utils._colourise = lambda s, colour: s

    for name, parser in APP._subparsers.choices.items():
        if name in cfg.sections:
            d = {}
            for k in cfg.options(name):
                try:
                    d[k] = cfg[name].as_bool(k)
                except ValueError:
                    d[k] = cfg[name][k]
            parser.set_defaults(**d)

    APP.arg('--version', action='version',
            version='%%(prog)s %s' % _version.dotted)
    APP.arg('-d', '--directory', metavar='dir',
            help=_('directory to read/write to'))
    APP.arg('--no-backup', dest='backup', action='store_true',
            help=_('do not write data file backups'))
    APP.arg('--config', metavar='file',
            help=_('file to read configuration data from'))

    APP.defaults(backup=not cfg['rdial'].as_bool('backup'),
                 directory=cfg['rdial']['directory'], config=cfg)
    try:
        APP.run(remaining)
    except utils.RdialError as error:
        print(utils.fail(error.message))
        return 2
