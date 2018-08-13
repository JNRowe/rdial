#
"""cmdline - Command line functionality for rdial."""
# Copyright © 2012-2018  James Rowe <jnrowe@gmail.com>
#                        Nathan McGregor <nathan.mcgregor@astrium.eads.net>
#
# This file is part of rdial.
#
# rdial is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# rdial is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# rdial.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0+

import datetime
import operator
import os
import shlex
import subprocess
from typing import Callable, List, Optional

import click
import tabulate

from jnrbase import colourise, i18n, iso_8601
from jnrbase.attrdict import AttrDict

from . import _version, utils
from .events import Event, Events, TaskNotRunningError, TaskRunningError

_, N_ = i18n.setup(_version)


class HiddenGroup(click.Group):

    """Support for 'hidden' commands.

    Any :obj:`click.Command` with the hidden attribute set will not be visible
    in help output.  This is mainly to be used for diagnostic commands, and
    shouldn’t be abused!

    """

    def list_commands(self, __ctx: click.Context) -> List[str]:
        """List visible commands.

        Args:
            __ctx: Current command context
        Returns:
            Visible command names
        """
        return sorted(k for k, v in self.commands.items()
                      if not hasattr(v, 'hidden'))


class TaskNameParamType(click.ParamType):

    """Task name parameter handler."""

    name = 'taskname'

    def convert(self, __value: str, __param: Optional[click.Argument],
                __ctx: Optional[click.Context]) -> str:
        """Check given task name is valid.

        Args:
            __value: Value given to flag
            __param: Parameter being processed
            __ctx: Current command context

        Returns:
            Valid task name

        """
        if not __value:
            raise click.BadParameter(_('No task name given'))
        if __value.startswith('-'):
            raise click.BadParameter(_('Task names with leading dashes are '
                                       'non-portable'))
        if __value.startswith('.') or '/' in __value or '\000' in __value:
            raise click.BadParameter(
                _('{!r} is not a valid task name').format(__value))
        # Should be based on platform’s PATH_MAX, but it isn’t exposed in a
        # clean way to Python
        if len(__value) > 255:
            raise click.BadParameter(
                _('{!r} is too long to be a valid task name(max 255 '
                  'characters)').format(__value))
        return __value


class StartTimeParamType(click.ParamType):

    """Start time parameter handler."""

    name = 'time'

    def convert(self, __value: str, __param: Optional[click.Argument],
                __ctx: Optional[click.Context]) -> datetime.datetime:
        """Check given start time is valid.

        Args:
            __value: Value given to flag
            __param: Parameter being processed
            __ctx: Current command context

        Returns:
            Valid start time

        """
        try:
            __value = utils.parse_datetime_user(__value)
        except ValueError:
            raise click.BadParameter(
                _('{!r} is not a valid ISO-8601 time string').format(__value))
        return __value


def task_from_dir(__ctx: click.Context, __param: click.Option,
                  __value: bool) -> None:
    """Override task name default using name of current directory.

    Args:
        __ctx: Current command context
        __param: Parameter being processed
        __value: True if flag given

    """
    if not __value or __ctx.resilient_parsing:
        return
    __param = [p for p in __ctx.command.params if p.name == 'task'][0]
    __param.default = os.path.basename(os.path.abspath(os.curdir))


def get_stop_message(__current: Event, __edit: bool = False) -> str:
    """Interactively fetch stop message.

    Args:
        __current: Current task
        __edit: Whether to edit existing message

    Returns:
        Message to use

    """
    marker = _('# Text below here ignored\n')
    task_message = _('# Task “{}” started {}Z').format(
        __current.task,
        iso_8601.format_datetime(__current.start))
    template = '{}\n{}{}'.format(__current.message, marker, task_message)
    message = click.edit(template, require_save=not __edit)
    if message is None:
        message = ''
    else:
        message = message.split(marker, 1)[0].rstrip('\n')
    return message


def task_option(__fun: Callable) -> Callable:
    """Add task selection options.

    Note:
        This is only here to reduce duplication in command setup.

    Args:
        __fun: Function to add options to

    Returns:
        Function with additional options

    """
    __fun = click.option('-x', '--from-dir', is_flag=True, expose_value=False,
                         is_eager=True, callback=task_from_dir,
                         help=_('Use directory name as task name.'))(__fun)
    __fun = click.argument('task', default='default', envvar='RDIAL_TASK',
                           required=False, type=TaskNameParamType())(__fun)
    return __fun


def duration_option(__fun: Callable) -> Callable:
    """Add duration selection option.

    Note:
        This is only here to reduce duplication in command setup.

    Args:
        __fun: Function to add options to

    Returns:
        Function with additional options

    """
    __fun = click.option(
        '-d', '--duration', default='all',
        type=click.Choice(['day', 'week', 'month', 'year', 'all']),
        help=_('Filter events for specified time period.'))(__fun)
    return __fun


def message_option(__fun: Callable) -> Callable:
    """Add message setting options.

    Note:
        This is only here to reduce duplication in command setup.

    Args:
        __fun: Function to add options to

    Returns:
        Function with additional options

    """
    __fun = click.option('-m', '--message', help=_('Closing message.'))(__fun)
    __fun = click.option('-F', '--file', 'fname', type=click.File(),
                         help=_('Read closing message from file.'))(__fun)
    return __fun


def hidden(__fun: click.Command) -> click.Command:
    """Add a hidden attribute to a Command object.

    :see:`HiddenGroup`.

    Args:
        __fun: Function to add hidden attribute to

    Returns:
        Function with hidden attribute set

    """
    __fun.hidden = True
    return __fun


# pylint: disable=too-many-arguments

@click.group(cls=HiddenGroup,
             help=_('Simple time tracking for simple people.'),
             epilog=_('Please report bugs at '
                      'https://github.com/JNRowe/rdial/issues'),
             context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(_version.dotted)
@click.option('-d', '--directory', metavar='DIR',
              type=click.Path(file_okay=False),
              help=_('Directory to read/write to.'))
@click.option('--backup/--no-backup', default=None,
              help=_('Do not write data file backups.'))
@click.option('--cache/--no-cache', default=None,
              help=_('Do not write cache files.'))
@click.option('--config', type=click.Path(exists=True, dir_okay=False,
                                          resolve_path=True, allow_dash=True),
              help=_('File to read configuration data from.'))
@click.option('-i', '--interactive/--no-interactive', default=None,
              help=_('Support interactive message editing.'))
@click.option('--colour/--no-colour', envvar='RDIAL_COLOUR', default=None,
              help=_('Output colourised informational text.'))
@click.pass_context
def cli(ctx: click.Context, directory: str, backup: bool, cache: bool,
        config: str, interactive: bool, colour: bool):
    """Main command entry point.

    Args:
        ctx: Current command context
        directory: Location to store event data
        backup: Whether to create backup files
        cache: Whether to create cache files
        config: Location of config file
        interactive: Whether to support interactive message editing
        colour: Whether to colourise output

    """
    cli_options = {
        'backup': backup,
        'cache': cache,
        'directory': directory,
        'interactive': interactive,
    }

    cfg = utils.read_config(config, cli_options)

    base = cfg['rdial']

    if colour is None:
        if 'color' in base:
            base['colour'] = base['color']
        colour = base.getboolean('colour')
    colourise.COLOUR = colour

    ctx.default_map = {}
    for name in ctx.command.commands:
        if name in cfg.sections():
            defs = {}
            for k in cfg[name]:
                try:
                    defs[k] = cfg[name].getboolean(k)
                except ValueError:
                    defs[k] = cfg[name][k]
            ctx.default_map[name] = defs

    ctx.obj = AttrDict(
        backup=base.getboolean('backup'),
        cache=base.getboolean('cache'),
        colour=colour,
        config=cfg,
        directory=base['directory'],
        interactive=base.getboolean('interactive'),
    )


def filter_events(__globs: AttrDict, __task: Optional[str] = None,
                  __duration: str = 'all') -> Events:
    """Filter events for report processing.

    Args:
        __globs: Global options object
        __task: Task name to filter on
        __duration: Time window to filter on

    Returns:
        Events: Events matching specified criteria

    """
    events = Events.read(__globs.directory, write_cache=__globs.cache)
    if __task:
        events = events.for_task(__task)
    if not __duration == 'all':  # pragma: no cover
        if __duration == 'week':
            today = datetime.date.today()
            events = events.for_week(*today.isocalendar()[:2])
        else:
            year, month, day = datetime.date.today().timetuple()[:3]
            if __duration == 'month':
                day = None
            elif __duration == 'year':
                month = None
                day = None
            events = events.for_date(year, month, day)
    return events


@hidden
@cli.command('bug-data', help=_('Produce data for rdial bug reports.'))
def bug_data():
    """Produce data for rdial bug reports."""
    import sys

    from pkg_resources import (DistributionNotFound, get_distribution)

    click.echo('* OS: {}'.format(sys.platform))
    click.echo('* `rdial` version: {}'.format(_version.dotted))
    click.echo('* `python` version: {}'.format(sys.version.replace('\n', '|')))
    click.echo()

    for m in ['click', 'cduration', 'jnrbase', 'tabulate']:
        try:
            pkg = get_distribution(m)
        except DistributionNotFound:
            continue
        link = utils.term_link(
            'https://pypi.org/project/{}/'.format(pkg.project_name),
            '`{}`'.format(pkg.project_name))
        click.echo('* {}: {}'.format(link, pkg.version))


@cli.command(help=_('Check storage consistency.'))
@click.pass_obj
@click.pass_context
def fsck(ctx: click.Context, globs: AttrDict):
    """Check storage consistency.

    Args:
        ctx: Current command context
        globs: Global options object

    """
    warnings = 0
    events = Events.read(globs.directory, write_cache=globs.cache)
    now = datetime.datetime.utcnow()
    lines = []
    # Note: progress is *four* times slower on my data and system
    with click.progressbar(events, label=_('Checking'),
                           fill_char=click.style(u'█', 'green'),
                           empty_char=click.style(u'·', 'yellow')) as pbar:
        last_event = next(pbar)
        for event in pbar:
            if not last_event.start + last_event.delta <= event.start:
                warnings += 1
                lines.append(colourise.fail(_('Overlap:')))
                lines.append(colourise.warn('   {!r}'.format(last_event)))
                lines.append(colourise.info('   {!r}'.format(event)))
            if event.start > now:
                warnings += 1
                lines.append(colourise.fail(_('Future start:')))
                lines.append(colourise.warn('   {!r}'.format(event)))
            elif event.start + event.delta > now:
                warnings += 1
                lines.append(colourise.fail(_('Future end:')))
                lines.append(colourise.warn('   {!r}'.format(event)))
            last_event = event
    if lines:
        click.echo_via_pager('\n'.join(lines))
        if warnings:
            # Will be success when 𝐱 % 256 == 0, so cap at 255
            ctx.exit(min(warnings, 255))


@cli.command(help=_('Start task.'))
@task_option
@click.option('-c', '--continue', 'continue_', is_flag=True,
              help=_('Restart previous task.'))
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@click.pass_obj
@utils.write_current
def start(globs: AttrDict, task: str, continue_: bool, new: bool,
          time: datetime):
    """Start task.

    Args:
        globs: Global options object
        taskk: Task name to operate on
        continue_: Pull task name from last running task
        new: Create a new task
        time: Task start time

    """
    with Events.wrapping(globs.directory, globs.backup, globs.cache) as events:
        if continue_:
            task = events.last().task
        events.start(task, new, time)


@cli.command(help=_('Stop task.'))
@message_option
@click.option('--amend', is_flag=True, help=_('Amend previous stop entry.'))
@click.pass_obj
@utils.remove_current
def stop(globs: AttrDict, message: str, fname: str, amend: bool):
    """Stop task.

    Args:
        globs: Global options object
        message: Message to assign to event
        fname: Filename to read message from
        amend: Amend a previously stopped event

    """
    if fname:
        message = fname.read()
    with Events.wrapping(globs.directory, globs.backup, globs.cache) as events:
        last_event = events.last()
        if last_event.running():
            if amend:
                raise TaskRunningError(
                    _('Can’t amend running task {}!').format(last_event.task))
        else:
            if not amend:
                raise TaskNotRunningError(_('No task running!'))
        if amend and not message:
            message = last_event.message
        if globs.interactive and not message:
            message = get_stop_message(last_event, amend)
        events.stop(message, force=amend)
    event = events.last()
    click.echo(_('Task {} running for {}').format(
        event.task,
        str(event.delta).split('.')[0]))


@cli.command(help=_('Switch to another task.'))
@task_option
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@message_option
@click.pass_obj
@utils.write_current
def switch(globs: AttrDict, task: str, new: bool, time: datetime,
           message: str, fname: str):
    """Complete last task and start new one.

    Args:
        globs: Global options object
        task: Task name to operate on
        new: Create a new task
        time: Task start time
        message: Message to assign to event
        fname: Filename to read message from

    """
    if fname:
        message = fname.read()
    with Events.wrapping(globs.directory, globs.backup, globs.cache) as events:
        event = events.last()
        if time and time < event.start:
            raise TaskNotRunningError(_('Can’t specify a start time before '
                                        'current task started!'))
        if not event.running():
            raise TaskNotRunningError(_('No task running!'))
        if new or task in events.tasks():
            if globs.interactive and not message:
                message = get_stop_message(event)
            # This is dirty, but we kick on to Events.start() to save
            # duplication of error handling for task names
            events.stop(message)
        events.last().delta = time - event.start
        events.start(task, new, time)
    click.echo(_('Task {} running for {}').format(
        event.task,
        str(event.delta).split('.')[0]))


@cli.command(help=_('Run command with timer.'))
@task_option
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@message_option
@click.option('-c', '--command', help=_('Command to run.'))
@click.pass_obj
def run(globs: AttrDict, task: str, new: bool, time: datetime, message: str,
        fname: str, command: str):
    """Run timed command.

    Args:
        globs: Global options object
        task: Task name to operate on
        new: Create a new task
        time: Task start time
        message: Message to assign to event
        fname: Filename to read message from
        command: Command to run

    """
    with Events.wrapping(globs.directory, globs.backup, globs.cache) as events:
        if events.running():
            raise TaskRunningError(
                _('Task {} is already started!').format(events.last().task))

        proc = subprocess.run(command, shell=True)

        events.start(task, new, time)
        with click.open_file('{}/.current'.format(globs.directory), 'w') as f:
            f.write(task)

        if fname:
            message = fname.read()
        if globs.interactive and not message:
            message = get_stop_message(events.last())
        events.stop(message)
    event = events.last()
    click.echo(_('Task {} running for {}').format(
        event.task,
        str(event.delta).split('.')[0]))
    os.unlink('{}/.current'.format(globs.directory))
    if proc.returncode != 0:
        raise OSError(proc.returncode, _('Command failed'))


@cli.command(help=_('Run predefined command with timer.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@message_option
@click.argument('wrapper', default='default')
@click.pass_obj
@click.pass_context
def wrapper(ctx: click.Context, globs: AttrDict, time: datetime, message: str,
            fname: str, wrapper: str):
    """Run predefined timed command.

    Args:
        ctx: Click context object
        globs: Global options object
        time: Task start time
        message: Message to assign to event
        fname: Filename to read message from
        wrapper: Run wrapper to execute

    """
    try:
        command = globs.config['run wrappers'][wrapper]
    except KeyError:
        raise click.BadParameter(_('No such wrapper {!r}').format(wrapper))
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
              envvar='RDIAL_REVERSE',
              help=_('Reverse sort order.'))
@click.option('--style', default='simple',
              type=click.Choice(tabulate._table_formats.keys()),
              help=_('Table output style.'))
@click.pass_obj
def report(globs: AttrDict, task: str, stats: bool, duration: str, sort: str,
           reverse: bool, style: str):
    """Report time tracking data.

    Args:
        globs: Global options object
        task: Task name to operate on
        stats: Display short overview of data
        duration: Time window to filter on
        sort: Key to sort events on
        reverse: Reverse sort order
        style: Table formatting style

    """
    if task == 'default':
        # Lazy way to remove duplicate argument definitions
        task = None
    events = filter_events(globs, task, duration)
    if stats:
        click.echo(N_('{} event in query', '{} events in query',
                      len(events)).format(len(events)))
        click.echo(_('Duration of events {}').format(events.sum()))
        if events:
            click.echo(_('First entry started at {}').format(events[0].start))
            click.echo(_('Last entry started at {}').format(events[-1].start))
        dates = set(e.start.date() for e in events)
        click.echo(_('Events exist on {:d} dates').format(len(dates)))
    else:
        data = sorted(([t, str(events.for_task(t).sum())]
                       for t in events.tasks()),
                      key=operator.itemgetter(['task', 'time'].index(sort)),
                      reverse=reverse)
        click.echo_via_pager(tabulate.tabulate(data, ['task', 'time'],
                                               tablefmt=style))
    if events.running():
        current = events.last()
        click.echo(_('Task “{}” started {}Z').format(
            current.task, iso_8601.format_datetime(current.start)))


@cli.command(help=_('Display running task, if any.'))
@click.pass_obj
def running(globs: AttrDict):
    """Display running task, if any.

    Args:
        globs: Global options object

    """
    events = Events.read(globs.directory, write_cache=globs.cache)
    if events.running():
        current = events.last()
        now = datetime.datetime.utcnow()
        click.echo(_('Task “{}” started {}').format(
            current.task, str(now - current.start).split('.')[0]))
    else:
        colourise.pwarn(_('No task is running!'))


@cli.command(help=_('Display last event, if any.'))
@click.pass_obj
def last(globs: AttrDict):
    """Display last event, if any.

    Args:
        globs: Global options object

    """
    events = Events.read(globs.directory, write_cache=globs.cache)
    event = events.last()
    if not events.running():
        click.echo(_('Last task {0.task}, ran for {0.delta}').format(event))
        if event.message:
            click.echo(event.message)
    else:
        colourise.pwarn(_('Task {.task} is still running').format(event))


@cli.command(help=_('Generate ledger compatible data file.'))
@task_option
@duration_option
@click.option('-r', '--rate', type=float, envvar='RDIAL_RATE',
              help=_('Hourly rate for task output.'))
@click.pass_obj
def ledger(globs: AttrDict, task: str, duration: str, rate: str):
    """Generate ledger compatible data file.

    Args:
        globs: Global options object
        task: Task name to operate on
        duration: Time window to filter on
        rate: Rate to assign hours in report

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
        hours = event.delta.total_seconds() / 3600
        lines.append('{}-{}'.format(event.start.strftime('%Y-%m-%d * %H:%M'),
                                    end.strftime('%H:%M')))
        lines.append('    (task:{})  {:.2f}h{}{}'.format(
            event.task, hours, ' @ {}'.format(rate) if rate else '',
            '  ; {}'.format(event.message) if event.message else ''))
    if events.running():
        lines.append(_(';; Running event not included in output!'))
    click.echo_via_pager('\n'.join(lines))

# pylint: enable=too-many-arguments


def main() -> int:
    """Command entry point to handle errors.

    Returns:
        Final exit code

    """
    try:
        # pylint: disable=no-value-for-parameter
        cli(auto_envvar_prefix='RDIAL')
        return 0
    except (ValueError, utils.RdialError) as error:
        colourise.pfail(str(error))
        return 2
    except OSError as error:
        return error.errno
