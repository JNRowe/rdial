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

import os
import shlex
import subprocess

import arrow
import click
import prettytable

from .events import (Events, TaskRunningError)
from .i18n import (_, N_)
from . import _version
from . import utils


class TaskNameParamType(click.ParamType):
    """Task name parameter handler."""
    name = 'taskname'

    def convert(self, value, param, ctx):
        """Check given task name is valid.

        :param str value: Value given to flag
        :param click.Argument param: Parameter being processed
        :param click.Context ctx: Current command context
        :rtype: :obj:`str`
        :return: Valid task name
        """
        if value.startswith('.') or '/' in value or '\000' in value:
            self.fail(_('%r is not a valid task name') % value)
        return value


class StartTimeParamType(click.ParamType):
    """Start time parameter handler."""
    name = 'time'

    def convert(self, value, param, ctx):
        """Check given start time is valid.

        :param str value: Value given to flag
        :param click.Argument param: Parameter being processed
        :param click.Context ctx: Current command context
        :rtype: :obj:`arrow.Arrow`
        :return: Valid start time
        """
        try:
            utils.parse_datetime(value)
        except arrow.parser.ParserError:
            self.fail(_('%r is not a valid ISO-8601 time string') % value)
        return value


def task_from_dir(ctx, value):
    """Override task name default using name of current directory.

    :param click.Context ctx: Current command context
    :param bool value: True if flag given
    """
    if value:
        param = [p for p in ctx.command.params if p.name == 'task'][0]
        param.default = os.path.basename(os.path.abspath(os.curdir))


def print_version(ctx, value):
    """Display rdial version.

    :param click.Context ctx: Current command context
    :param bool value: True if flag given
    """
    if value:
        print('rdial %s' % _version.dotted)
        ctx.exit()


@click.group(help=_('Simple time tracking for simple people.'),
             epilog=_('Please report bugs to '
                      'https://github.com/JNRowe/rdial/issues'))
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help=_('show version string and exit'))
@click.option('-d', '--directory', metavar='DIR',
              help=_('directory to read/write to'))
@click.option('--backup/--no-backup',
              help=_('do not write data file backups'))
@click.option('--config', type=click.File(),
              help=_('file to read configuration data from'))
@click.pass_context
def cli(ctx, directory, backup, config):
    """Main command entry point.

    :param click.Context ctx: Current command context
    :param str directory: Location to store event data
    :param bool backup: Whether to create backup files
    :param str config: Location of config file
    """
    cfg = utils.read_config(config)

    if 'color' in cfg['rdial']:
        cfg['rdial']['colour'] = cfg['rdial']['color']
    if not cfg['rdial'].as_bool('colour') or os.getenv('NO_COLOUR') \
            or os.getenv('NO_COLOR'):
        utils._colourise = lambda s, colour: s

    ctx.default_map = {}
    for name in ctx.command.commands:
        if name in cfg.sections:
            d = {}
            for k in cfg[name]:
                try:
                    d[k] = cfg[name].as_bool(k)
                except ValueError:
                    d[k] = cfg[name][k]
            ctx.default_map[name] = d

    ctx.obj = {
        'backup': backup if backup else cfg['rdial'].as_bool('backup'),
        'directory': directory if directory else cfg['rdial']['directory'],
        'config': cfg,
    }


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


@cli.command(help=_('check storage consistency'))
@click.pass_obj
def fsck(globs):
    """Check storage consistency.

    :param dict globs: Global options object
    """
    with Events.context(globs['directory'], globs['backup']) as events:
        last = events[0]
        for event in events[1:]:
            if not last.start + last.delta <= event.start:
                print(utils.fail(_('Overlap:')))
                print(utils.warn('  %r' % last))
                print('  %r' % event)
            last = event


@cli.command(help=_('start task'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('use directory name as task name'))
@click.argument('task', default='default', required=False,
                type=TaskNameParamType())
@click.option('-n', '--new', is_flag=True, help=_('start a new task'))
@click.option('-t', '--time', default='', help=_('set start time'),
              type=StartTimeParamType())
@click.pass_obj
@utils.write_current
def start(globs, task, new, time):
    """Start task.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param arrow.Arrow time: Task start time
    """
    with Events.context(globs['directory'], globs['backup']) as events:
        events.start(task, new, time)


@cli.command(help=_('stop task'))
@click.option('-m', '--message', help=_('closing message'))
@click.option('-F', '--file', type=click.File(),
              help=_('read closing message from file'))
@click.option('--amend', is_flag=True, help=_('amend previous stop entry'))
@click.pass_obj
@utils.remove_current
def stop(globs, message, file, amend):
    """Stop task.

    :param dict globs: Global options object
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    :param bool amend: Amend a previously stopped event
    """
    if file:
        message = file.read()
    with Events.context(globs['directory'], globs['backup']) as events:
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


@cli.command(help=_('switch to another task'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('use directory name as task name'))
@click.argument('task', default='default', required=False,
                type=TaskNameParamType())
@click.option('-n', '--new', is_flag=True, help=_('start a new task'))
@click.option('-m', '--message',
              help=_('closing message for current task'))
@click.option('-F', '--file', type=click.File(),
              help=_('read closing message for current task from file'))
@click.pass_obj
@utils.write_current
def switch(globs, task, new, message, file):
    """Complete last task and start new one.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    """
    if file:
        message = file.read()
    with Events.context(globs['directory'], globs['backup']) as events:
        if new or task in events.tasks():
            # This is dirty, but we kick on to Events.start() to save
            # duplication of error handling for task names
            events.stop(message)
        event = events.last()
        events.start(task, new)
    print(_('Task %s running for %s') % (event.task,
                                         str(event.delta).split('.')[0]))


@cli.command(help=_('run command with timer'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('use directory name as task name'))
@click.argument('task', default='default', required=False,
                type=TaskNameParamType())
@click.option('-n', '--new', is_flag=True, help=_('start a new task'))
@click.option('-t', '--time', default='', help=_('set start time'),
              type=StartTimeParamType())
@click.option('-m', '--message', help=_('closing message'))
@click.option('-F', '--file', type=click.File(),
              help=_('read closing message from file'))
@click.option('-c', '--command', help=_('command to run'))
@click.pass_obj
def run(globs, task, new, time, message, file, command):
    """Run timed command.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param arrow.Arrow time: Task start time
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    :param str command: Command to run
    """
    with Events.context(globs['directory'], globs['backup']) as events:
        if events.running():
            raise TaskRunningError(_('Task %s is already started!'
                                     % events.last().task))

        try:
            p = subprocess.Popen(command, shell=True)
        except OSError as e:
            raise utils.RdialError(e.strerror)

        events.start(task, new, time)
        open('%s/.current' % globs['directory'], 'w').write(task)

        p.wait()

        if file:
            message = file.read()
        events.stop(message)
    event = events.last()
    print(_('Task %s running for %s') % (event.task,
                                         str(event.delta).split('.')[0]))
    os.unlink('%s/.current' % globs['directory'])
    if p.returncode != 0:
        raise OSError(p.returncode, _('Command failed'))


@cli.command(help=_('run predefined command with timer'))
@click.option('-t', '--time', default='', help=_('set start time'),
              type=StartTimeParamType())
@click.option('-m', '--message', help=_('closing message'))
@click.option('-F', '--file', type=click.File(),
              help=_('read closing message from file'))
@click.argument('wrapper', default='default')
@click.pass_obj
@click.pass_context
def wrapper(ctx, globs, time, message, file, wrapper):
    """Run predefined timed command.

    :param click.Context ctx: Click context object
    :param dict globs: Global options object
    :param datetime.datetime time: Task start time
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    :param str wrapper: Run wrapper to execute
    """
    if not 'run wrappers' in globs['config']:
        raise ValueError(_('No %r section in config') % 'run wrappers')
    try:
        command = globs['config']['run wrappers'][wrapper]
    except KeyError:
        raise ValueError(_('No such wrapper %r') % wrapper)
    parser = ctx.parent.command.commands['run'].make_parser(ctx)
    args = {'time': time, 'message': message, 'file': file, 'new': False}
    args.update(parser.parse_args(shlex.split(command))[0])
    ctx.invoke(run, **args)


@cli.command(help=_('report time tracking data'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('use directory name as task name'))
@click.argument('task', default='default', required=False,
                type=TaskNameParamType())
@click.option('--html', 'output', flag_value='html',
              help=_('produce HTML output'))
@click.option('--human', 'output', flag_value='human',
              help=_('produce human-readable output'))
@click.option('-d', '--duration', default='all',
              type=click.Choice(['day', 'week', 'month', 'year', 'all']),
              help=_('filter events for specified time period'))
@click.option('-s', '--sort', default='task',
              type=click.Choice(['task', 'time']), help=_('field to sort by'))
@click.option('-r', '--reverse/--no-reverse', help=_('reverse sort order'))
@click.pass_obj
def report(globs, task, output, duration, sort, reverse):
    """Report time tracking data.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param str output: Type of output to produce
    :param str duration: Time window to filter on
    :param str sort: Key to sort events on
    :param bool reverse: Reverse sort order
    """
    if task == 'default':
        # Lazy way to remove duplicate argument definitions
        task = None
    events = filter_events(globs['directory'], task, duration)
    if output == 'human':
        print(N_('%d event in query', '%d events in query', len(events))
              % len(events))
        print(_('Duration of events %s') % events.sum())
        print(_('First entry started at %s') % events[0].start)
        print(_('Last entry started at %s') % events[-1].start)
        dates = set(e.start.date() for e in events)
        print(_('Events exist on %d dates') % len(dates))
    else:
        table = prettytable.PrettyTable(['task', 'time'])
        if output == 'html':
            formatter = table.get_html_string
        else:
            formatter = table.get_string
        try:
            table.align['task'] = 'l'
        except AttributeError:  # prettytable 0.5 compatibility
            table.set_field_align('task', 'l')
        for task in events.tasks():
            table.add_row([task, events.for_task(task).sum()])

        print(formatter(sortby=sort, reversesort=reverse))
    if events.running() and not output == 'html':
        current = events.last()
        print(_("Task `%s' started %s")
              % (current.task, current.start.humanize()))


@cli.command(help=_('display running task, if any'))
@click.pass_obj
def running(globs):
    """Display running task, if any.

    :param dict globs: Global options object
    """
    events = Events.read(globs['directory'])
    if events.running():
        current = events.last()
        print(_("Task `%s' started %s") % (current.task,
                                           current.start.humanize()))
    else:
        print(utils.warn(_('No task is running!')))


@cli.command(help=_('display last event, if any'))
@click.pass_obj
def last(globs):
    """Display last event, if any.

    :param dict globs: Global options object
    """
    events = Events.read(globs['directory'])
    event = events.last()
    if not events.running():
        print(_('Last task %s, ran for %s') % (event.task, event.delta))
        if event.message:
            print(repr(event.message))
    else:
        print(utils.warn(_('Task %s is still running') % event.task))


@cli.command(help=_('generate ledger compatible data file'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('use directory name as task name'))
@click.argument('task', default='default', required=False,
                type=TaskNameParamType())
@click.option('-d', '--duration', default='all',
              type=click.Choice(['day', 'week', 'month', 'year', 'all']),
              help=_('filter events for specified time period'))
@click.option('-r', '--rate', type=click.FLOAT,
              help=_('hourly rate for task output'))
@click.pass_obj
def ledger(globs, task, duration, rate):
    """Generate ledger compatible data file.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param str duration: Time window to filter on
    :param str rate: Rate to assign hours in report
    """
    if task == 'default':
        # Lazy way to remove duplicate argument definitions
        task = None
    events = filter_events(globs['directory'], task, duration)
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
    """Command entry point to handle errors.

    :rtype: :obj:`int`
    :return: Final exit code
    """
    try:
        cli()
        return 0
    except (ValueError, utils.RdialError) as error:
        print(utils.fail(error.message))
        return 2
    except OSError as error:
        return error.errno
