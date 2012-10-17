#
#
"""cmdline - Command line functionality for rdial"""
# Copyright (C) 2011-2012  James Rowe <jnrowe@gmail.com>
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

import argparse
import datetime
import os

import isodate
import prettytable

from .events import Events
from . import _version
from . import utils


def filter_events(directory, task=None, duration=None):
    """Filter events for report processing.

    :param argparse.Namespace args: Command line arguments
    :rtype: `Events`
    :return: Events matching criteria specified in ``args``

    """
    events = Events.read(directory)
    if task:
        events = events.for_task(task)
    if not duration == "all":
        if duration == "week":
            today = datetime.date.today()
            events = events.for_week(*today.isocalendar()[:2])
        else:
            year, month, day = datetime.date.today().timetuple()[:3]
            if duration == "month":
                day = None
            elif duration == "year":
                month = None
                day = None
            events = events.for_date(year, month, day)
    return events


def start_time_typecheck(string):
    """Check given start time is valid."""
    try:
        utils.parse_datetime(string)
    except ValueError:
        raise argparse.ArgumentTypeError('%r is not a valid ISO-8601 time '
                                         'string' % string)
    return string


def task_name_typecheck(string):
    """Check given task name is valid."""
    if '/' in string:
        raise argparse.ArgumentTypeError('%r is not a valid task name'
                                         % string)
    return string


def process_command_line():
    """Process command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0].split('-', 1)[1],
        epilog='Please report bugs to jnrowe@gmail.com',
        version='%%(prog)s %s' % _version.dotted)

    parser.add_argument('-d', '--directory', default=utils.xdg_data_location(),
                        metavar='dir',
                        help='directory to read/write to (%(default)s)')

    subs = parser.add_subparsers(title='subcommands')

    start_p = subs.add_parser('start', help='start task')
    start_p.add_argument('-n', '--new', action='store_true',
                         help='start a new task')
    start_p.add_argument('-t', '--time', help='set start time', default='',
                         type=start_time_typecheck)
    dirname = os.path.basename(os.path.abspath(os.curdir))
    start_p.add_argument('-d', '--from-dir', action='store_true',
                         help='use directory name as task [%s]' % dirname)
    start_p.add_argument('task', default='default', nargs='?',
                         help='task name', type=task_name_typecheck)
    start_p.set_defaults(func=start)

    stop_p = subs.add_parser('stop', help='stop task')
    stop_p.add_argument('-m', '--message', help='closing message')
    stop_p.add_argument('--amend', action='store_true',
                        help='amend previous stop entry')
    stop_p.set_defaults(func=stop)

    report_p = subs.add_parser('report', help='report time tracking data')
    report_p.add_argument('-d', '--duration', default='all',
                          choices=['day', 'week', 'month', 'year', 'all'],
                          help=('filter events for specified time period '
                                '[%(default)s]'))
    report_p.add_argument('-s', '--sort', default='task',
                          choices=['task', 'time'],
                          help='field to sort by [%(default)s]')
    report_p.add_argument('-r', '--reverse', action='store_true',
                          help='reverse sort order')
    report_p.add_argument('--html', action='store_true',
                          help='produce HTML output')
    report_p.add_argument('--human', action='store_true',
                          help='produce human-readable output')
    report_p.add_argument('task', nargs='?', help='task name',
                          type=task_name_typecheck)
    report_p.set_defaults(func=report)

    running_p = subs.add_parser('running', help='display running task, if any')
    running_p.set_defaults(func=running)

    last_p = subs.add_parser('last', help='display last event, if any')
    last_p.set_defaults(func=last)

    ledger_p = subs.add_parser('ledger',
                               help='generate ledger compatible data file')
    ledger_p.add_argument('-d', '--duration', default='all',
                          choices=['day', 'week', 'month', 'year', 'all'],
                          help=('filter events for specified time period '
                                '[%(default)s]'))
    ledger_p.add_argument('-r', '--rate', help='hourly rate for task output')
    ledger_p.add_argument('task', nargs='?', help='task name',
                          type=task_name_typecheck)
    ledger_p.set_defaults(func=ledger)

    return parser.parse_args()


def start(args):
    """Start task."""
    if args.from_dir:
        args.task = os.path.basename(os.path.abspath(os.curdir))
    with Events.context(args.directory) as events:
        events.start(args.task, args.new, args.time)


def stop(args):
    """Stop task."""
    with Events.context(args.directory) as events:
        if args.amend and not args.message:
            event = events.last()
            args.message = event.message
        events.stop(args.message, force=args.amend)
    event = events.last()
    print('Task %s running for %s' % (event.task, event.delta))


def report(args):
    """Report time tracking data."""
    events = filter_events(args.directory, args.task, args.duration)
    if args.human:
        print('%d events in query' % len(events))
        print('Duration of events %s' % events.sum())
        print('First entry started at %s' % events[0].start)
        print('Last entry started at %s' % events[-1].start)
        dates = set(e.start.date() for e in events)
        print('Events exist on %d dates' % len(dates))
    else:
        table = prettytable.PrettyTable(['task', 'time'])
        formatter = table.get_html_string if args.html else table.get_string
        try:
            table.align['task'] = 'l'
        except AttributeError:  # prettytable 0.5 compatibility
            table.set_field_align('task', 'l')
        for task in events.tasks():
            table.add_row([task, events.for_task(task).sum()])

        print(formatter(sortby=args.sort, reversesort=args.reverse))
    if events.running() and not args.html:
        current = events.last()
        print("Currently running `%s' since %s"
              % (current.task, isodate.datetime_isoformat(current.start)))


def running(args):
    """Display running task, if any."""
    events = Events.read(args.directory)
    if events.running():
        current = events.last()
        print('Currently running %s since %s'
            % (current.task, isodate.datetime_isoformat(current.start)))
    else:
        print('No task is running!')


def last(args):
    """Display last event, if any."""
    events = Events.read(args.directory)
    event = events.last()
    if not events.running():
        print('Last task %s, ran for %s' % (event.task, event.delta))
    else:
        print('Task %s is still running' % event.task)


def ledger(args):
    """Generate ledger compatible data file."""
    events = filter_events(args.directory, args.task, args.duration)
    if events.running():
        print(';; Currently running event not included in output!')
    for event in events:
        if not event.delta:
            break
        end = event.start + event.delta
        # Can't use timedelta.total_seconds() as it was only added in 2.7
        seconds = event.delta.days * 86400 + event.delta.seconds
        hours = seconds / 3600.0
        print('%s-%s' % (event.start.strftime('%Y-%m-%d * %H:%M'),
                         end.strftime('%H:%M')))
        print('    (task:%s)  %.2fh%s'
              % (event.task, hours, ' @ %s' % args.rate if args.rate else ''))
    if events.running():
        print(';; Currently running event not included in output!')


def main():
    """Main script."""
    args = process_command_line()
    try:
        args.func(args)
    except utils.RdialError as error:
        print('Error: %s' % error)
        return 2
