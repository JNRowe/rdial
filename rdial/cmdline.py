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

import aaargh
import isodate
import prettytable

from .events import Events
from . import _version
from . import utils


APP = aaargh.App(description=__doc__.splitlines()[0].split("-", 1)[1],
                 epilog="Please report bugs to jnrowe@gmail.com",
                 version="%%(prog)s %s" % _version.dotted)


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
    if '/' in string or '\000' in string:
        raise argparse.ArgumentTypeError('%r is not a valid task name'
                                         % string)
    return string


@APP.cmd
@APP.cmd_arg('task', default='default', nargs='?', help='task name',
             type=task_name_typecheck)
@APP.cmd_arg('-n', '--new', action='store_true', help='start a new task')
@APP.cmd_arg('-t', '--time', default='', help='set start time',
             type=start_time_typecheck)
@APP.cmd_arg('-d', '--from-dir', action='store_true',
             help='use directory name as task')
def start(directory, task, new, time, from_dir):
    """start task"""
    if from_dir:
        task = os.path.basename(os.path.abspath(os.curdir))
    with Events.context(directory) as events:
        events.start(task, new, time)


@APP.cmd
@APP.cmd_arg('-m', '--message', help='closing message')
@APP.cmd_arg('--amend', action='store_true', default=False,
             help='amend previous stop entry')
def stop(directory, message, amend):
    """stop task"""
    with Events.context(directory) as events:
        if amend and not message:
            last = events.last()
            message = last.message
        events.stop(message, force=amend)
    last = events.last()
    print('Task %s running for %s' % (last.task, last.delta))


@APP.cmd
@APP.cmd_arg('task', nargs='?', help='task name', type=task_name_typecheck)
@APP.cmd_arg('-d', '--duration', default='all',
             choices=['day', 'week', 'month', 'year', 'all'],
             help="filter events for specified time period")
@APP.cmd_arg('-s', '--sort', default='task', choices=['task', 'time'],
             help='field to sort by')
@APP.cmd_arg('-r', '--reverse', default=False, help='reverse sort order')
@APP.cmd_arg('--html', default=False, help='produce HTML output')
@APP.cmd_arg('--human', default=False, help='produce human-readable output')
def report(directory, task, duration, sort, reverse, html, human):
    """report time tracking data"""
    events = filter_events(directory, task, duration)
    if human:
        print('%d events in query' % len(events))
        print('Duration of events %s' % events.sum())
        print('First entry started at %s' % events[0].start)
        print('Last entry started at %s' % events[-1].start)
        dates = set(e.start.date() for e in events)
        print('Events exist on %d dates' % len(dates))
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
        print("Currently running `%s' since %s"
              % (current.task, isodate.datetime_isoformat(current.start)))


@APP.cmd
def running(directory):
    """display running task, if any"""
    events = Events.read(directory)
    if events.running():
        current = events.last()
        print('Currently running %s since %s'
            % (current.task, isodate.datetime_isoformat(current.start)))
    else:
        print('No task is running!')


@APP.cmd
def last(directory):
    """display last event, if any"""
    events = Events.read(directory)
    last = events.last()
    if not events.running():
        print('Last task %s, ran for %s' % (last.task, last.delta))
    else:
        print('Task %s is still running' % last.task)


@APP.cmd
@APP.cmd_arg('task', nargs='?', help='task name', type=task_name_typecheck)
@APP.cmd_arg('-d', '--duration', default='all',
             choices=['day', 'week', 'month', 'year', 'all'],
             help="filter events for specified time period")
@APP.cmd_arg('-r', '--rate', help='hourly rate for task output')
def ledger(directory, task, duration, rate):
    """generate ledger compatible data file"""
    events = filter_events(directory, task, duration)
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
              % (event.task, hours, ' @ %s' % rate if rate else ''))
    if events.running():
        print(';; Currently running event not included in output!')


def main():
    """Main script."""
    APP.arg('-d', '--directory', default=utils.xdg_data_location(),
            metavar='dir', help='directory to read/write to')
    try:
        APP.run()
    except utils.RdialError as e:
        APP._parser.error(e)
