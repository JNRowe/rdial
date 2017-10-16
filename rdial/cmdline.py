#
"""cmdline - Command line functionality for rdial."""
# Copyright © 2012-2017  James Rowe <jnrowe@gmail.com>
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

import datetime
import operator
import os
import shlex
import subprocess

import click
import tabulate

from jnrbase import colourise, i18n, iso_8601
from jnrbase.attrdict import AttrDict

from . import _version, utils
from .events import Events, TaskNotRunningError, TaskRunningError

_, N_ = i18n.setup(_version)


class HiddenGroup(click.Group):

    """Support for 'hidden' commands.

    Any :obj:`click.Command` with the hidden attribute set will not be visible
    in help output.  This is mainly to be used for diagnostic commands, and
    shouldn’t be abused!

    """

    def list_commands(self, ctx):
        """List visible commands.

        Args:
            ctx (click.Context): Current command context
        Returns:
            list: Visible command names
        """
        return sorted(k for k, v in self.commands.items()
                      if not hasattr(v, 'hidden'))


class TaskNameParamType(click.ParamType):

    """Task name parameter handler."""

    name = 'taskname'

    def convert(self, value, param, ctx):
        """Check given task name is valid.

        Args:
            value (str): Value given to flag
            param (click.Argument): Parameter being processed
            ctx (click.Context): Current command context

        Returns:
            str: Valid task name

        """
        if not value:
            raise click.BadParameter(_('No task name given'))
        if value.startswith('-'):
            raise click.BadParameter(_('Task names with leading dashes are '
                                       'non-portable'))
        if value.startswith('.') or '/' in value or '\000' in value:
            raise click.BadParameter(
                _('{!r} is not a valid task name').format(value))
        # Should be based on platform’s PATH_MAX, but it isn’t exposed in a
        # clean way to Python
        if len(value) > 255:
            raise click.BadParameter(
                _('{!r} is too long to be a valid task name(max 255 '
                  'characters)').format(value))
        return value


class StartTimeParamType(click.ParamType):

    """Start time parameter handler."""

    name = 'time'

    def convert(self, value, param, ctx):
        """Check given start time is valid.

        Args:
            value (str): Value given to flag
            param (click.Argument): Parameter being processed
            ctx (click.Context): Current command context

        Returns:
            datetime.datetime: Valid start time

        """
        try:
            value = utils.parse_datetime_user(value)
        except ValueError:
            raise click.BadParameter(
                _('{!r} is not a valid ISO-8601 time string').format(value))
        return value


def task_from_dir(ctx, param, value):
    """Override task name default using name of current directory.

    Args:
        ctx (click.Context): Current command context
        param (click.Argument): Parameter being processed
        value (bool): True if flag given

    """
    if not value or ctx.resilient_parsing:
        return
    param = [p for p in ctx.command.params if p.name == 'task'][0]
    param.default = os.path.basename(os.path.abspath(os.curdir))


def get_stop_message(current, edit=False):
    """Interactively fetch stop message.

    Args:
        current (events.Event): Current task
        edit (bool): Whether to edit existing message

    Returns:
        str: Message to use

    """
    marker = _('# Text below here ignored\n')
    task_message = _('# Task “{}” started {}').format(
        current.task,
        iso_8601.format_datetime(current.start))
    template = '{}\n{}{}'.format(current.message, marker, task_message)
    message = click.edit(template, require_save=not edit)
    if message is None:
        message = ''
    else:
        message = message.split(marker, 1)[0].rstrip('\n')
    return message


def task_option(fun):
    """Add task selection options.

    Note:
        This is only here to reduce duplication in command setup.

    Args:
        fun (types.FunctionType): Function to add options to

    Returns:
        types.FunctionType: Function with additional options

    """
    fun = click.option('-x', '--from-dir', is_flag=True, expose_value=False,
                       is_eager=True, callback=task_from_dir,
                       help=_('Use directory name as task name.'))(fun)
    fun = click.argument('task', default='default', envvar='RDIAL_TASK',
                         required=False, type=TaskNameParamType())(fun)
    return fun


def duration_option(fun):
    """Add duration selection option.

    Note:
        This is only here to reduce duplication in command setup.

    Args:
        fun (types.FunctionType): Function to add options to

    Returns:
        types.FunctionType: Function with additional options

    """
    fun = click.option('-d', '--duration', default='all',
                       type=click.Choice(['day', 'week', 'month', 'year',
                                          'all']),
                       help=_('Filter events for specified time period.'))(fun)
    return fun


def message_option(fun):
    """Add message setting options.

    Note:
        This is only here to reduce duplication in command setup.

    Args:
        fun (types.FunctionType): Function to add options to

    Returns:
        types.FunctionType: Function with additional options

    """
    fun = click.option('-m', '--message', help=_('Closing message.'))(fun)
    fun = click.option('-F', '--file', 'fname', type=click.File(),
                       help=_('Read closing message from file.'))(fun)
    return fun


def hidden(fun):
    """Add a hidden attribute to a Command object.

    :see:`HiddenGroup`.

    Args:
        fun (types.FunctionType): Function to add hidden attribute to

    Returns:
        types.FunctionType: Function with hidden attribute set

    """
    fun.hidden = True
    return fun


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
def cli(ctx, directory, backup, cache, config, interactive, colour):
    """Main command entry point.

    Args:
        ctx (click.Context): Current command context
        directory (str): Location to store event data
        backup (bool): Whether to create backup files
        cache (bool): Whether to create cache files
        config (str): Location of config file
        interactive (bool): Whether to support interactive message editing

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


def filter_events(globs, task=None, duration='all'):
    """Filter events for report processing.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object
        task (str): Task name to filter on
        duration (str): Time window to filter on

    Returns:
        Events: Events matching specified criteria

    """
    events = Events.read(globs.directory, write_cache=globs.cache)
    if task:
        events = events.for_task(task)
    if not duration == 'all':  # pragma: no cover
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

    for m in ['click', 'ciso8601', 'cduration', 'tabulate']:
        try:
            pkg = get_distribution(m)
        except DistributionNotFound:
            continue
        link = utils.term_link(
            'https://pypi.python.org/pypi/{}'.format(pkg.project_name),
            '`{}`'.format(pkg.project_name))
        click.echo('* {}: {}'.format(link, pkg.version))


@cli.command(help=_('Check storage consistency.'))
@click.pass_obj
@click.pass_context
def fsck(ctx, globs):
    """Check storage consistency.

    Args:
        ctx (click.Context): Current command context
        globs (~jnrbase.attrdict.AttrDict): Global options object

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
@click.option('-n', '--new', is_flag=True, help=_('Start a new task.'))
@click.option('-t', '--time', default='', help=_('Set start time.'),
              type=StartTimeParamType())
@click.pass_obj
@utils.write_current
def start(globs, task, new, time):
    """Start task.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object
        task (str): Task name to operate on
        new (bool): Create a new task
        time (datetime.datetime): Task start time

    """
    with Events.wrapping(globs.directory, globs.backup, globs.cache) as events:
        events.start(task, new, time)


@cli.command(help=_('Stop task.'))
@message_option
@click.option('--amend', is_flag=True, help=_('Amend previous stop entry.'))
@click.pass_obj
@utils.remove_current
def stop(globs, message, fname, amend):
    """Stop task.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object
        message (str): Message to assign to event
        fname (str): Filename to read message from
        amend (bool): Amend a previously stopped event

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
            message = get_stop_message(last_event, edit=amend)
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
def switch(globs, task, new, time, message, fname):
    """Complete last task and start new one.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object
        task (str): Task name to operate on
        new (bool): Create a new task
        time (datetime.datetime): Task start time
        message (str): Message to assign to event
        fname (str): Filename to read message from

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
def run(globs, task, new, time, message, fname, command):
    """Run timed command.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object
        task (str): Task name to operate on
        new (bool): Create a new task
        time (datetime.datetime): Task start time
        message (str): Message to assign to event
        fname (str): Filename to read message from
        command (str): Command to run

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
def wrapper(ctx, globs, time, message, fname, wrapper):
    """Run predefined timed command.

    Args:
        ctx (click.Context): Click context object
        globs (~jnrbase.attrdict.AttrDict): Global options object
        time (datetime.datetime): Task start time
        message (str): Message to assign to event
        fname (str): Filename to read message from
        wrapper (str): Run wrapper to execute

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
def report(globs, task, stats, duration, sort, reverse, style):
    """Report time tracking data.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object
        task (str): Task name to operate on
        stats (bool): Display short overview of data
        duration (str): Time window to filter on
        sort (str): Key to sort events on
        reverse (bool): Reverse sort order
        style (str): Table formatting style

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
        click.echo(_('Task “{}” started {}').format(
            current.task, iso_8601.format_datetime(current.start)))


@cli.command(help=_('Display running task, if any.'))
@click.pass_obj
def running(globs):
    """Display running task, if any.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object

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
def last(globs):
    """Display last event, if any.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object

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
def ledger(globs, task, duration, rate):
    """Generate ledger compatible data file.

    Args:
        globs (~jnrbase.attrdict.AttrDict): Global options object
        task (str): Task name to operate on
        duration (str): Time window to filter on
        rate (str): Rate to assign hours in report

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
        # Can’t use timedelta.total_seconds() as it was only added in 2.7
        seconds = event.delta.days * 86400 + event.delta.seconds
        hours = seconds / 3600
        lines.append('{}-{}'.format(event.start.strftime('%Y-%m-%d * %H:%M'),
                                    end.strftime('%H:%M')))
        lines.append('    (task:{})  {:.2f}h{}{}'.format(
            event.task, hours, ' @ {}'.format(rate) if rate else '',
            '  ; {}'.format(event.message) if event.message else ''))
    if events.running():
        lines.append(_(';; Running event not included in output!'))
    click.echo_via_pager('\n'.join(lines))

# pylint: enable=too-many-arguments


def main():
    """Command entry point to handle errors.

    Returns:
        int: Final exit code

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
