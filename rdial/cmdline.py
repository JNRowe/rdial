#
# coding=utf-8
"""cmdline - Command line functionality for rdial."""
# Copyright © 2011-2015  James Rowe <jnrowe@gmail.com>
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
        if not value:
            self.fail(_('No task name given'))
        if value.startswith('.') or '/' in value or '\000' in value:
            self.fail(_('%r is not a valid task name') % value)
        # Should be based on platform's PATH_MAX, but it isn't exposed in a
        # clean way to Python
        if len(value) > 255:
            self.fail(_('%r is too long to be a valid task name') % value)
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
            value = utils.parse_datetime_user(value)
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


def get_stop_message(current, edit=False):
    """Interactively fetch stop message.

    :param events.Event current: Current task
    :param bool edit: Whether to edit existing message
    :rtype: :obj:`str`
    :return: Message to use
    """
    marker = _('# Text below here ignored\n')
    task_message = _("# Task `%s' started %s") % (current.task,
                                                  current.start.humanize())
    template = "%s\n%s%s" % (current.message, marker, task_message)
    message = click.edit(template, require_save=not edit)
    if message is None:
        message = ''
    else:
        message = message.split(marker, 1)[0].rstrip('\n')
    return message


def task_option(fun):
    """Add task selection options.

    :param function fun: Function to add options to
    :rtype: :obj:`func`
    :return: Function with additional options
    """
    fun = click.option('-x', '--from-dir', is_flag=True, expose_value=False,
                       is_eager=True, callback=task_from_dir,
                       help=_('Use directory name as task name.'))(fun)
    fun = click.argument('task', default='default', envvar='RDIAL_TASK',
                         required=False, type=TaskNameParamType())(fun)
    return fun


def duration_option(fun):
    """Add duration selection option.

    .. note:: This is only here to reduce duplication in command setup.

    :param function fun: Function to add options to
    :rtype: :obj:`func`
    :return: Function with additional options
    """
    fun = click.option('-d', '--duration', default='all',
                       type=click.Choice(['day', 'week', 'month', 'year',
                                          'all']),
                       help=_('Filter events for specified time period.'))(fun)
    return fun


def message_option(fun):
    """Add message setting options.

    :param function fun: Function to add options to
    :rtype: :obj:`func`
    :return: Function with additional options
    """
    fun = click.option('-m', '--message', help=_('Closing message.'))(fun)
    fun = click.option('-F', '--file', 'fname', type=click.File(),
                       help=_('Read closing message from file.'))(fun)
    return fun


# pylint: disable=too-many-arguments

@click.group(help=_('Simple time tracking for simple people.'),
             epilog=_('Please report bugs at '
                      'https://github.com/JNRowe/rdial/issues'),
             context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(_version.dotted)
@click.option('-d', '--directory', envvar='RDIAL_DIRECTORY', metavar='DIR',
              type=click.Path(file_okay=False),
              help=_('Directory to read/write to.'))
@click.option('--backup/--no-backup', envvar='RDIAL_BACKUP',
              help=_('Do not write data file backups.'))
@click.option('--cache/--no-cache', envvar='RDIAL_CACHE',
              help=_('Do not write cache files.'))
@click.option('--config', envvar='RDIAL_CONFIG',
              type=click.Path(exists=True, dir_okay=False, resolve_path=True),
              help=_('File to read configuration data from.'))
@click.option('-i', '--interactive/--no-interactive',
              envvar='RDIAL_INTERACTIVE',
              help=_('Support interactive message editing.'))
@click.pass_context
def cli(ctx, directory, backup, cache, config, interactive):
    """Main command entry point.

    :param click.Context ctx: Current command context
    :param str directory: Location to store event data
    :param bool backup: Whether to create backup files
    :param bool cache: Whether to create cache files
    :param str config: Location of config file
    :param bool interactive: Whether to support interactive message editing
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
            defs = {}
            for k in cfg[name]:
                try:
                    defs[k] = cfg[name].as_bool(k)
                except ValueError:
                    defs[k] = cfg[name][k]
            ctx.default_map[name] = defs

    ctx.obj = utils.AttrDict(
        backup=backup or base.as_bool('backup'),
        cache=cache or base.as_bool('cache'),
        config=cfg,
        directory=directory or base['directory'],
        interactive=interactive or base.as_bool('interactive'),
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
    events = Events.read(globs.directory, write_cache=globs.cache)
    lines = []
    with click.progressbar(events, label=_('Checking'),
                           fill_char=click.style('#', 'green')) as pbar:
        last_event = pbar.next()
        for event in pbar:
            if not last_event.start + last_event.delta <= event.start:
                warnings += 1
                lines.append(click.style(_('Overlap:'), 'red'))
                lines.append(click.style(_('   %r') % last_event, 'yellow'))
                lines.append(click.style(_('   %r') % event, 'green'))
            last_event = event
    if lines:
        click.echo_via_pager('\n'.join(lines))
        if warnings:
            ctx.exit(warnings)


@cli.command(help=_('Start task.'))
@task_option
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
@message_option
@click.option('--amend', is_flag=True, help=_('Amend previous stop entry.'))
@click.pass_obj
@utils.remove_current
def stop(globs, message, fname, amend):
    """Stop task.

    :param dict globs: Global options object
    :param str message: Message to assign to event
    :param str fname: Filename to read message from
    :param bool amend: Amend a previously stopped event
    """
    if fname:
        message = fname.read()
    with Events.context(globs.directory, globs.backup, globs.cache) as events:
        last_event = events.last()
        if last_event.running():
            if amend:
                raise TaskRunningError(_("Can't amend running task %s!")
                                       % last_event.task)
        else:
            if not amend:
                raise TaskNotRunningError(_('No task running!'))
        if amend and not message:
            message = last_event.message
        if globs.interactive and not message:
            get_stop_message(last_event, edit=amend)
        events.stop(message, force=amend)
    event = events.last()
    click.echo(_('Task %s running for %s') % (event.task,
                                              str(event.delta).split('.')[0]))


@cli.command(help=_('Switch to another task.'))
@task_option
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@message_option
@click.pass_obj
@utils.write_current
def switch(globs, task, new, time, message, fname):
    """Complete last task and start new one.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param datetime.datetime time: Task start time
    :param str message: Message to assign to event
    :param str fname: Filename to read message from
    """
    if fname:
        message = fname.read()
    with Events.context(globs.directory, globs.backup, globs.cache) as events:
        event = events.last()
        if time and time < event.start:
            raise TaskNotRunningError(_("Can't specify a start time before "
                                        "current task started!"))
        if not event.running():
            raise TaskNotRunningError(_('No task running!'))
        if new or task in events.tasks():
            if globs.interactive and not message:
                get_stop_message(event)
            # This is dirty, but we kick on to Events.start() to save
            # duplication of error handling for task names
            events.stop(message)
        events.last().delta = time - event.start
        events.start(task, new, time)
    click.echo(_('Task %s running for %s') % (event.task,
                                              str(event.delta).split('.')[0]))


@cli.command(help=_('Run command with timer.'))
@task_option
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@message_option
@click.option('-c', '--command', help=_('Command to run.'))
@click.pass_obj
def run(globs, task, new, time, message, fname, command):
    """Run timed command.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool new: Create a new task
    :param datetime.datetime time: Task start time
    :param str message: Message to assign to event
    :param str fname: Filename to read message from
    :param str command: Command to run
    """
    with Events.context(globs.directory, globs.backup, globs.cache) as events:
        if events.running():
            raise TaskRunningError(_('Task %s is already started!'
                                     % events.last().task))

        try:
            proc = subprocess.Popen(command, shell=True)
        except OSError as err:
            raise utils.RdialError(err.strerror)

        events.start(task, new, time)
        with click.open_file('%s/.current' % globs.directory, 'w') as f:
            f.write(task)

        proc.wait()

        if fname:
            message = fname.read()
        if globs.interactive and not message:
            get_stop_message(events.running())
        events.stop(message)
    event = events.last()
    click.echo(_('Task %s running for %s') % (event.task,
                                              str(event.delta).split('.')[0]))
    os.unlink('%s/.current' % globs.directory)
    if proc.returncode != 0:
        raise OSError(proc.returncode, _('Command failed'))


@cli.command(help=_('Run predefined command with timer.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@message_option
@click.argument('wrapper', default='default')
@click.pass_obj
@click.pass_context
def wrapper(ctx, globs, time, message, fname, wrapper):
    """Run predefined timed command.

    :param click.Context ctx: Click context object
    :param dict globs: Global options object
    :param datetime.datetime time: Task start time
    :param str message: Message to assign to event
    :param str fname: Filename to read message from
    :param str wrapper: Run wrapper to execute
    """
    if 'run wrappers' not in globs.config:
        raise ValueError(_('No %r section in config') % 'run wrappers')
    try:
        command = globs.config['run wrappers'][wrapper]
    except KeyError:
        raise ValueError(_('No such wrapper %r') % wrapper)
    parser = ctx.parent.command.commands['run'].make_parser(ctx)
    args = {'time': time, 'message': message, 'fname': fname, 'new': False}
    args.update(parser.parse_args(shlex.split(command))[0])
    ctx.invoke(run, **args)  # pylint: disable=star-args


@cli.command(help=_('Report time tracking data.'))
@task_option
@click.option('--stats', is_flag=True,
              help=_('Display database statistics.'))
@duration_option
@click.option('-s', '--sort', default='task', envvar='RDIAL_SORT',
              type=click.Choice(['task', 'time']), help=_('Field to sort by.'))
@click.option('-r', '--reverse/--no-reverse', default=False,
              envvar='RDIAL_REVERSE', help=_('Reverse sort order.'))
@click.option('--style', default='simple', envvar='RDIAL_TABLE_STYLE',
              type=click.Choice(tabulate._table_formats.keys()),
              help=_('Table output style.'))
@click.pass_obj
def report(globs, task, stats, duration, sort, reverse, style):
    """Report time tracking data.

    :param dict globs: Global options object
    :param str task: Task name to operate on
    :param bool stats: Display short overview of data
    :param str duration: Time window to filter on
    :param str sort: Key to sort events on
    :param bool reverse: Reverse sort order
    :param str style: Table formatting style
    """
    if task == 'default':
        # Lazy way to remove duplicate argument definitions
        task = None
    events = filter_events(globs, task, duration)
    if stats:
        click.echo(N_('%d event in query', '%d events in query', len(events))
                   % len(events))
        click.echo(_('Duration of events %s') % events.sum())
        if events:
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
            click.echo(event.message)
    else:
        utils.warn(_('Task %s is still running') % event.task)


@cli.command(help=_('Generate ledger compatible data file.'))
@task_option
@duration_option
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

# pylint: enable=too-many-arguments


def main():
    """Command entry point to handle errors.

    :rtype: :obj:`int`
    :return: Final exit code
    """
    try:
        cli()  # pylint: disable=no-value-for-parameter
        return 0
    except (ValueError, utils.RdialError) as error:
        utils.fail(error.message)
        return 2
    except OSError as error:
        return error.errno
