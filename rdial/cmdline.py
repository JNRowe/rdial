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

import datetime
import operator
import os
import shlex
import subprocess

import click
import tabulate

from .events import (Events, TaskNotRunningError, TaskRunningError)
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
        :rtype: :obj:`datetime.datetime`
        :return: Valid start time
        """
        try:
            value = utils.parse_datetime(value)
        except ValueError:
            self.fail(_('%r is not a valid ISO-8601 time string') % value)
        return value


def task_from_dir(ctx, param, value):
    """Override task name default using name of current directory.

    :param click.Context ctx: Current command context
    :param click.Argument param: Parameter being processed
    :param bool value: True if flag given
    """
    if value:
        param = [p for p in ctx.command.params if p.name == 'task'][0]
        param.default = os.path.basename(os.path.abspath(os.curdir))


@click.group(help=_('Simple time tracking for simple people.'),
             epilog=_('Please report bugs to '
                      'https://github.com/JNRowe/rdial/issues'))
@click.version_option(_version.dotted)
@click.option('-d', '--directory', envvar='RDIAL_DIRECTORY', metavar='DIR',
              help=_('Directory to read/write to.'))
@click.option('--backup/--no-backup', envvar='RDIAL_BACKUP',
              help=_('Do not write data file backups.'))
@click.option('--cache/--no-cache', envvar='RDIAL_CACHE',
              help=_('Do not write cache files.'))
@click.option('--config', envvar='RDIAL_CONFIG', type=click.File(),
              help=_('File to read configuration data from.'))
@click.pass_context
def cli(ctx, directory, backup, cache, config):
    """Main command entry point.

    :param click.Context ctx: Current command context
    :param str directory: Location to store event data
    :param bool backup: Whether to create backup files
    :param bool cache: Whether to create cache files
    :param str config: Location of config file
    """
    cfg = utils.read_config(config)
    base = cfg['rdial']

    if 'color' in base:
        base['colour'] = base['color']
    if not base.as_bool('colour') or os.getenv('NO_COLOUR') \
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

    ctx.obj = utils.AttrDict(
        backup=backup or base.as_bool('backup'),
        cache=cache or base.as_bool('cache'),
        config=cfg,
        directory=directory or base['directory'],
    )


def filter_events(globs, task=None, duration=None):
    """Filter events for report processing.

    :param dict globs: Global options object
    :param str task: Task name to filter on
    :param str duration: Time window to filter on
    :rtype: :obj:`rdial.events.Events`
    :return: Events matching specified criteria
    """
    events = Events.read(globs.directory, write_cache=globs.cache)
    if task:
        events = events.for_task(task)
    if not duration == 'all':
        if duration == 'week':
            today = datetime.date.today()
            events = events.for_week(*today.isocalendar()[:2])
        else:
            year, month, day = datetime.date.today().timetuple()[:3]
            if duration == 'month':
                day = None
            elif duration == 'year':
                month = None
                day = None
            events = events.for_date(year, month, day)
    return events


@cli.command(help=_('Check storage consistency.'))
@click.pass_obj
@click.pass_context
def fsck(ctx, globs):
    """Check storage consistency.

    :param click.Context ctx: Current command context
    :param dict globs: Global options object
    """
    warnings = 0
    with Events.context(globs.directory, globs.backup, globs.cache) as events:
        last = events[0]
        for event in events[1:]:
            if not last.start + last.delta <= event.start:
                warnings += 1
                utils.fail(_('Overlap:'))
                utils.warn('  %r' % last)
                click.echo('  %r' % event)
            last = event
    if warnings:
        ctx.exit(warnings)


@cli.command(help=_('Start task.'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('Use directory name as task name.'))
@click.argument('task', default='default', envvar='RDIAL_TASK',
                required=False, type=TaskNameParamType())
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@click.pass_obj
@utils.write_current
def start(globs, task, new, time):
    """Start task.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param datetime.datetime time: Task start time
    """
    with Events.context(globs.directory, globs.backup, globs.cache) as events:
        events.start(task, new, time)


@cli.command(help=_('Stop task.'))
@click.option('-m', '--message', help=_('Closing message.'))
@click.option('-F', '--file', type=click.File(),
              help=_('Read closing message from file.'))
@click.option('--amend', is_flag=True, help=_('Amend previous stop entry.'))
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
    with Events.context(globs.directory, globs.backup, globs.cache) as events:
        last = events.last()
        if amend and last.running():
            raise TaskRunningError(_("Can't amend running task %s!")
                                   % last.task)
        if amend and not message:
            event = events.last()
            message = event.message
        events.stop(message, force=amend)
    event = events.last()
    click.echo(_('Task %s running for %s') % (event.task,
                                              str(event.delta).split('.')[0]))


@cli.command(help=_('Switch to another task.'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('Use directory name as task name.'))
@click.argument('task', default='default', envvar='RDIAL_TASK',
                required=False, type=TaskNameParamType())
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@click.option('-m', '--message',
              help=_('Closing message for current task.'))
@click.option('-F', '--file', type=click.File(),
              help=_('Read closing message for current task from file.'))
@click.pass_obj
@utils.write_current
def switch(globs, task, new, time, message, file):
    """Complete last task and start new one.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param datetime.datetime time: Task start time
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    """
    if file:
        message = file.read()
    with Events.context(globs.directory, globs.backup, globs.cache) as events:
        event = events.last()
        if time and time < event.start:
            raise TaskNotRunningError(_("Can't specify a start time before "
                                        "current task started!"))
        if new or task in events.tasks():
            # This is dirty, but we kick on to Events.start() to save
            # duplication of error handling for task names
            events.stop(message)
        events.last().delta = time - event.start
        events.start(task, new, time)
    click.echo(_('Task %s running for %s') % (event.task,
                                              str(event.delta).split('.')[0]))


@cli.command(help=_('Run command with timer.'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('Use directory name as task name.'))
@click.argument('task', default='default', envvar='RDIAL_TASK',
                required=False, type=TaskNameParamType())
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@click.option('-m', '--message', help=_('Closing message.'))
@click.option('-F', '--file', type=click.File(),
              help=_('Read closing message from file.'))
@click.option('-c', '--command', help=_('Command to run.'))
@click.pass_obj
def run(globs, task, new, time, message, file, command):
    """Run timed command.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param datetime.datetime time: Task start time
    :param str message: Message to assign to event
    :param str file: Filename to read message from
    :param str command: Command to run
    """
    with Events.context(globs.directory, globs.backup, globs.cache) as events:
        if events.running():
            raise TaskRunningError(_('Task %s is already started!'
                                     % events.last().task))

        try:
            p = subprocess.Popen(command, shell=True)
        except OSError as e:
            raise utils.RdialError(e.strerror)

        events.start(task, new, time)
        open('%s/.current' % globs.directory, 'w').write(task)

        p.wait()

        if file:
            message = file.read()
        events.stop(message)
    event = events.last()
    click.echo(_('Task %s running for %s') % (event.task,
                                              str(event.delta).split('.')[0]))
    os.unlink('%s/.current' % globs.directory)
    if p.returncode != 0:
        raise OSError(p.returncode, _('Command failed'))


@cli.command(help=_('Run predefined command with timer.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@click.option('-m', '--message', help=_('Closing message.'))
@click.option('-F', '--file', type=click.File(),
              help=_('Read closing message from file.'))
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
    if not 'run wrappers' in globs.config:
        raise ValueError(_('No %r section in config') % 'run wrappers')
    try:
        command = globs.config['run wrappers'][wrapper]
    except KeyError:
        raise ValueError(_('No such wrapper %r') % wrapper)
    parser = ctx.parent.command.commands['run'].make_parser(ctx)
    args = {'time': time, 'message': message, 'file': file, 'new': False}
    args.update(parser.parse_args(shlex.split(command))[0])
    ctx.invoke(run, **args)


@cli.command(help=_('Report time tracking data.'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('Use directory name as task name.'))
@click.argument('task', default='default', envvar='RDIAL_TASK',
                required=False, type=TaskNameParamType())
@click.option('--human', help=_('Produce human-readable output.'))
@click.option('-d', '--duration', default='all',
              type=click.Choice(['day', 'week', 'month', 'year', 'all']),
              help=_('Filter events for specified time period.'))
@click.option('-s', '--sort', default='task', envvar='RDIAL_SORT',
              type=click.Choice(['task', 'time']), help=_('Field to sort by.'))
@click.option('-r', '--reverse/--no-reverse', default=False,
              envvar='RDIAL_REVERSE', help=_('Reverse sort order.'))
@click.option('--style', default='simple', envvar='RDIAL_TABLE_STYLE',
              type=click.Choice(tabulate._table_formats.keys()),
              help=_('Table output style.'))
@click.pass_obj
def report(globs, task, human, duration, sort, reverse, style):
    """Report time tracking data.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool human: Display short overview of data
    :param str duration: Time window to filter on
    :param str sort: Key to sort events on
    :param bool reverse: Reverse sort order
    :param str style: Table formatting style
    """
    if task == 'default':
        # Lazy way to remove duplicate argument definitions
        task = None
    events = filter_events(globs, task, duration)
    if human:
        click.echo(N_('%d event in query', '%d events in query', len(events))
                   % len(events))
        click.echo(_('Duration of events %s') % events.sum())
        click.echo(_('First entry started at %s') % events[0].start)
        click.echo(_('Last entry started at %s') % events[-1].start)
        dates = set(e.start.date() for e in events)
        click.echo(_('Events exist on %d dates') % len(dates))
    else:
        data = sorted(([t, str(events.for_task(t).sum())]
                       for t in events.tasks()),
                      key=operator.itemgetter(['task', 'time'].index(sort)),
                      reverse=reverse)
        click.echo_via_pager(tabulate.tabulate(data, ['task', 'time'],
                                               tablefmt=style))
    if events.running():
        current = events.last()
        click.echo(_("Task `%s' started %s")
                   % (current.task, utils.format_datetime(current.start)))


@cli.command(help=_('Display running task, if any.'))
@click.pass_obj
def running(globs):
    """Display running task, if any.

    :param dict globs: Global options object
    """
    events = Events.read(globs.directory, write_cache=globs.cache)
    if events.running():
        current = events.last()
        click.echo(_("Task `%s' started %s")
                   % (current.task,
                      str(utils.utcnow() - current.start).split('.')[0]))
    else:
        utils.warn(_('No task is running!'))


@cli.command(help=_('Display last event, if any.'))
@click.pass_obj
def last(globs):
    """Display last event, if any.

    :param dict globs: Global options object
    """
    events = Events.read(globs.directory, write_cache=globs.cache)
    event = events.last()
    if not events.running():
        click.echo(_('Last task %s, ran for %s') % (event.task, event.delta))
        if event.message:
            click.echo(repr(event.message))
    else:
        utils.warn(_('Task %s is still running') % event.task)


@cli.command(help=_('Generate ledger compatible data file.'))
@click.option('-x', '--from-dir', is_flag=True, expose_value=False,
              is_eager=True, callback=task_from_dir,
              help=_('Use directory name as task name.'))
@click.argument('task', default='default', envvar='RDIAL_TASK',
                required=False, type=TaskNameParamType())
@click.option('-d', '--duration', default='all',
              type=click.Choice(['day', 'week', 'month', 'year', 'all']),
              help=_('Filter events for specified time period.'))
@click.option('-r', '--rate', envvar='RDIAL_RATE', type=click.FLOAT,
              help=_('Hourly rate for task output.'))
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
    events = filter_events(globs, task, duration)
    lines = []
    if events.running():
        lines.append(_(';; Running event not included in output!'))
    for event in events:
        if not event.delta:
            continue
        end = event.start + event.delta
        # Can't use timedelta.total_seconds() as it was only added in 2.7
        seconds = event.delta.days * 86400 + event.delta.seconds
        hours = seconds / 3600.0
        lines.append('%s-%s' % (event.start.strftime('%Y-%m-%d * %H:%M'),
                                end.strftime('%H:%M')))
        lines.append('    (task:%s)  %.2fh%s'
                     % (event.task, hours, ' @ %s' % rate if rate else ''))
    if events.running():
        lines.append(_(';; Running event not included in output!'))
    click.echo_via_pager('\n'.join(lines))


def main():
    """Command entry point to handle errors.

    :rtype: :obj:`int`
    :return: Final exit code
    """
    try:
        cli()
        return 0
    except (ValueError, utils.RdialError) as error:
        utils.fail(error.message)
        return 2
    except OSError as error:
        return error.errno
