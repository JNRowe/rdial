#
#
"""rdial - Simple time tracking for simple people"""
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

from . import _version


__version__ = _version.dotted
__date__ = _version.date
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2011-2012  James Rowe <jnrowe@gmail.com>"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See git repository"

from email.utils import parseaddr

# pylint: disable-msg=W0622
__doc__ += """.

A simple time tracking tool, with no frills and no fizzy coating.

.. moduleauthor:: `%s <mailto:%s>`__
""" % parseaddr(__author__)

import csv
import contextlib
import datetime
import glob
import inspect
import operator
import os
import sys
import tempfile

import aaargh
import isodate
import prettytable


APP = aaargh.App(description=__doc__.splitlines()[0].split("-", 1)[1],
                 epilog="Please report bugs to jnrowe@gmail.com",
                 version="%%(prog)s %s" % __version__)


class RdialError(ValueError):

    """Generic exception for rdial."""

    pass


class TaskNotRunningError(RdialError):

    """Exception for calling mutators when a task is not running."""

    pass


class TaskRunningError(RdialError):

    """Exception for starting task when a task is already running."""

    pass


class Event(object):

    """Base object for handling database event."""

    def __init__(self, task, start="", delta="", message=""):
        """Initialise a new ``Event`` object.

        :param str task: Task name to tracking
        :param str start: ISO-8601 start time for event
        :param str delta: ISO-8601 duration for event
        :param str message: Message to attach to event

        """
        self.task = task
        self.start = parse_datetime(start)
        self.delta = parse_delta(delta)
        self.message = message

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: `str`
        :return: Event representation suitable for ``eval()``

        """
        return 'Event(%r, %r, %r, %r)' \
            % (self.task, isodate.datetime_isoformat(self.start),
               format_delta(self.delta), self.message)

    def writer(self):
        """Prepare object for export.

        :rtype: `dict`
        :return: Event data for object storage

        """
        return {
            'start': isodate.datetime_isoformat(self.start),
            'delta': format_delta(self.delta),
            'message': self.message,
        }

    def running(self):
        """Check if event is running.

        :rtype: `str`
        :return: Event name, if running

        """
        if self.delta == datetime.timedelta(0):
            return self.task
        return False

    def stop(self, message=None, force=False):
        """Stop currently running event.

        :param str message: Message to attach to event
        :param bool force: Re-stop a previously stopped event
        :raise TaskNotRunningError: Event not running

        """
        if not force and self.delta:
            raise TaskNotRunningError('No task currently running!')
        self.delta = utcnow() - self.start
        self.message = message
FIELDS = inspect.getargspec(Event.__init__)[0][2:]


class Events(list):

    """Container for database events."""

    def __init__(self, iterable=None):
        """Initialise a new ``Events`` object.

        :param list iterable: Objects to add to container

        """
        super(Events, self).__init__(iterable if iterable else [])
        self._dirty = set()

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: `str`
        :return: Events representation suitable for ``eval()``

        """
        return 'Events(%s)' % super(self.__class__, self).__repr__()

    @staticmethod
    def read(directory):
        """Read and parse database.

        Assume a new ``Events`` object should be created if the file is missing

        :param str directory: Location to read database files from
        :rtype: `Events`
        :returns: Parsed events database

        """
        if not os.path.exists(directory):
            return Events()
        events = []
        for file in glob.glob('%s/*.csv' % directory):
            task = os.path.basename(file)[:-4]
            events.extend(Event(task, **d)
                          for d in list(csv.DictReader(open(file))))
        return Events(sorted(events, key=operator.attrgetter('start')))

    def write(self, directory):
        """Write database file.

        :param str directory: Location to write database files to

        """
        if not os.path.isdir(directory):
            os.mkdir(directory)

        for task in self._dirty:
            events = self.for_task(task)
            if sys.version_info[0] == 3:
                temp = tempfile.NamedTemporaryFile(mode='w', newline='',
                                                   prefix='.', dir=directory,
                                                   delete=False)
                writer = csv.DictWriter(temp, FIELDS)
            else:
                temp = tempfile.NamedTemporaryFile(prefix='.', dir=directory,
                                                   delete=False)
                writer = csv.DictWriter(temp, FIELDS, lineterminator='\n')
            # Can't use writeheader, it wasn't added until 2.7.
            writer.writerow(dict(zip(FIELDS, FIELDS)))
            for event in events:
                writer.writerow(event.writer())
            os.rename(temp.name, "%s/%s.csv" % (directory, task))

    def tasks(self):
        """Generate a list of tasks in the database.

        :rtype: `list` of `str`
        :return: Names of tasks in database

        """
        return sorted(set(event.task for event in self))

    def last(self):
        """Return current/last event.

        This handles the empty database case by returning ``None``

        :rtype: `Event`
        :return: Last recorded event

        """
        if len(self) > 0:
            return self[-1]
        else:
            return None

    def running(self):
        """Check if an event is running.

        We return the currently running task, if one exists, for easy access.

        :rtype: `Event`
        :return: Running event, if an event running

        """
        last = self.last()
        return last.running() if last else False

    def start(self, task, start=''):
        """Start a new event.

        :param str task: Task name to tracking
        :param str start: ISO-8601 start time for event
        :raise TaskRunningError: An event is already running

        """
        running = self.running()
        if running:
            raise TaskRunningError('Currently running task %s!' % running)
        self.append(Event(task, start))
        self._dirty.add(task)

    def stop(self, message=None, force=False):
        """Stop currently running event.

        :param str message: Message to attach to event
        :param bool force: Re-stop a previously stopped event
        :raise TaskNotRunningError: No task currently running!

        """
        if not force and not self.running():
            raise TaskNotRunningError('No task currently running!')
        self.last().stop(message, force)
        self._dirty.add(self.last().task)

    def filter(self, filt):
        """Apply filter to events.

        :param func filt: Function to filter with
        :rtype: `Events`
        :return: Events matching given filter function

        """
        return Events(filter(filt, self))

    def for_task(self, task):
        """Filter events for a specific task.

        :param str task: Task name to filter on
        :rtype: `Events`
        :return: Events marked with given task name

        """
        return self.filter(lambda x: x.task == task)

    def for_date(self, year, month=None, day=None):
        """Filter events for a specific day.

        :param int year: Year to filter on
        :param int month: Month to filter on, or ``None``
        :param int day: Day to filter on, or ``None``
        :rtype: `Events`
        :return: Events occurring within specified date

        """
        events = self.filter(lambda x: x.start.year == year)
        if month:
            events = events.filter(lambda x: x.start.month == month)
        if day:
            events = events.filter(lambda x: x.start.day == day)
        return events

    def for_week(self, year, week):
        """Filter events for a specific ISO-2015 week.

        ISO-2015 defines a week as Monday to Sunday, with the first week of
        a year being the first week containing a Thursday.

        :param int year: Year to filter events on
        :param int week: ISO-2015 month number to filter events on
        :rtype: `Events`
        :return: Events occurring in given ISO-2015 week

        """
        bound = datetime.date(year, 1, 4)
        iso_start = bound - datetime.timedelta(days=bound.isocalendar()[1])
        start = iso_start + datetime.timedelta(weeks=week - 1)
        end = start + datetime.timedelta(days=7)
        return self.filter(lambda x: start <= x.start.date() < end)

    def sum(self):
        """Sum duration of all events.

        :rtype: `datetime.timedelta`
        :return: Sum of all event deltas

        """
        return sum(map(lambda x: x.delta, self), datetime.timedelta(0))

    @staticmethod
    @contextlib.contextmanager
    def context(directory):
        """Convenience context handler to manage reading and writing database.

        :param str directory: Database location

        """
        events = Events.read(directory)
        yield events
        if events._dirty:
            events.write(directory)


def parse_delta(string):
    """Parse ISO-8601 duration string.

    :param str string: Duration string to parse
    :rtype: `datetime.timedelta`
    :return: Parsed delta object

    """
    if not string:
        return datetime.timedelta(0)
    return isodate.parse_duration(string)


def format_delta(timedelta_):
    """Format ISO-8601 duration string.

    :param datetime.timedelta timedelta_: Duration to process
    :rtype: `str`
    :return: ISO-8601 representation of duration

    """
    if timedelta_ == datetime.timedelta(0):
        return ""
    return isodate.duration_isoformat(timedelta_)


def parse_datetime(string):
    """Parse ISO-8601 datetime string.

    :param str string: Datetime string to parse
    :rtype: `datetime.datetime`
    :return: Parsed datetime object

    """
    if string == "":
        datetime_ = utcnow()
    else:
        datetime_ = isodate.parse_datetime(string)
        if datetime_.tzinfo:
            datetime_ = datetime_.astimezone(isodate.UTC)
        else:
            datetime_ = datetime_.replace(tzinfo=isodate.UTC)
    return datetime_


def utcnow():
    """Wrapper for producing timezone aware current timestamp.

    :rtype: `datetime.datetime`
    :return: Current date and time, in UTC

    """
    return datetime.datetime.utcnow().replace(tzinfo=isodate.UTC)


def xdg_data_location():
    """Return a data location honouring $XDG_DATA_HOME.

    :rtype: `str`

    """
    user_dir = os.getenv('XDG_DATA_HOME', os.path.join(os.getenv('HOME', '/'),
                         '.local/share'))
    return os.path.join(user_dir, 'rdial')


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


@APP.cmd
@APP.cmd_arg('task', default='default', nargs='?', help='task name')
@APP.cmd_arg('-t', '--time', default='', help='set start time')
def start(directory, task, time):
    """start task"""
    with Events.context(directory) as events:
        events.start(task, time)


@APP.cmd
@APP.cmd_arg('-m', '--message', help='closing message')
@APP.cmd_arg('--amend', default=False, help='amend previous stop entry')
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
@APP.cmd_arg('task', nargs='?', help='task name')
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
    last = events.last()
    if events.running():
        print('Currently running %s since %s'
              % (last.task, isodate.datetime_isoformat(last.start)))
    else:
        print('Last task %s, ran for %s' % (last.task, last.delta))


@APP.cmd
@APP.cmd_arg('task', nargs='?', help='task name')
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
    APP.arg('-d', '--directory', default=xdg_data_location(),
            metavar='dir', help='directory to read/write to')
    try:
        APP.run()
    except RdialError as e:
        APP._parser.error(e)
