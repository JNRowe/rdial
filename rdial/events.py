#
#
"""events - Event models for rdial"""
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

# pylint: disable-msg=C0121

import contextlib
import csv
import datetime
import glob
import inspect
import operator
import os
import sys
import tempfile

import isodate

from . import utils


class TaskNotRunningError(utils.RdialError):

    """Exception for calling mutators when a task is not running."""

    pass


class TaskRunningError(utils.RdialError):

    """Exception for starting task when a task is already running."""

    pass


class TaskNotExistError(utils.RdialError):

    """Exception for attempting to operate on a non-existing task."""

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
        self.start = utils.parse_datetime(start)
        self.delta = utils.parse_delta(delta)
        self.message = message

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: `str`
        :return: Event representation suitable for ``eval()``

        """
        return 'Event(%r, %r, %r, %r)' \
            % (self.task, isodate.datetime_isoformat(self.start),
               utils.format_delta(self.delta), self.message)

    def writer(self):
        """Prepare object for export.

        :rtype: `dict`
        :return: Event data for object storage

        """
        return {
            'start': isodate.datetime_isoformat(self.start),
            'delta': utils.format_delta(self.delta),
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
        """Stop running event.

        :param str message: Message to attach to event
        :param bool force: Re-stop a previously stopped event
        :raise TaskNotRunningError: Event not running

        """
        if not force and self.delta:
            raise TaskNotRunningError('No task running!')
        self.delta = utils.utcnow() - self.start
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

        We return the running task, if one exists, for easy access.

        :rtype: `Event`
        :return: Running event, if an event running

        """
        last = self.last()
        return last.running() if last else False

    def start(self, task, new=False, start=''):
        """Start a new event.

        :param str task: Task name to tracking
        :param str start: ISO-8601 start time for event
        :raise TaskRunningError: An event is already running

        """
        running = self.running()
        if running:
            raise TaskRunningError('Running task %s!' % running)
        if not new and task not in self.tasks():
            raise TaskNotExistError("Task %s does not exist!  Use `--new' to "
                                    "create it" % task)
        self.append(Event(task, start))
        self._dirty.add(task)

    def stop(self, message=None, force=False):
        """Stop running event.

        :param str message: Message to attach to event
        :param bool force: Re-stop a previously stopped event
        :raise TaskNotRunningError: No task running!

        """
        if not force and not self.running():
            raise TaskNotRunningError('No task running!')
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
