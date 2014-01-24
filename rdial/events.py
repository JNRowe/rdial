#
# coding=utf-8
"""events - Event models for rdial"""
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

import contextlib
import csv
import datetime
import glob
import inspect
import operator
import os
import sys
import tempfile

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

    def __init__(self, task, start=None, delta=None, message=''):
        """Initialise a new ``Event`` object.

        :param str task: Task name to tracking
        :param datetime.datetime start: Start time for event
        :param datetime.timedelta delta: Duration for event
        :param str message: Message to attach to event

        """
        self.task = task
        if isinstance(start, datetime.datetime):
            if not start.tzinfo:
                raise ValueError('Must not be a naive datetime %r' % start)
            self.start = start
        else:
            self.start = utils.parse_datetime(start)
        if isinstance(delta, datetime.timedelta):
            self.delta = delta
        else:
            self.delta = utils.parse_delta(delta)
        self.message = message

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: :obj:`str`
        :return: Event representation suitable for :func:`eval`

        """
        return 'Event(%r, %r, %r, %r)' \
            % (self.task, utils.format_datetime(self.start),
               utils.format_delta(self.delta), self.message)

    def writer(self):
        """Prepare object for export.

        :rtype: :obj:`dict`
        :return: Event data for object storage

        """
        return {
            'start': utils.format_datetime(self.start),
            'delta': utils.format_delta(self.delta),
            'message': self.message,
        }

    def running(self):
        """Check if event is running.

        :rtype: :obj:`str`
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

    def __init__(self, iterable=None, backup=True):
        """Initialise a new ``Events`` object.

        :param list iterable: Objects to add to container
        :param bool backup: Whether to create backup files

        """
        super(Events, self).__init__(iterable if iterable else [])
        self.backup = backup
        self._dirty = []

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: :obj:`str`
        :return: Events representation suitable for :func:`eval`

        """
        return 'Events(%s)' % super(self.__class__, self).__repr__()

    @property
    def dirty(self):
        """Tasks requiring sync against storage."""
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        """Mark task as needing sync.

        :param str value: Task to mark as dirty

        """
        if not value in self._dirty:
            self._dirty.append(value)

    @dirty.deleter
    def dirty(self):
        """Mark dirty queue as flushed."""
        self._dirty = []

    @staticmethod
    def read(directory, backup=True):
        """Read and parse database.

        Assume a new :obj:`Events` object should be created if the file is
        missing

        :param str directory: Location to read database files from
        :param bool backup: Whether to create backup files
        :rtype: :obj:`Events`
        :returns: Parsed events database

        """
        if not os.path.exists(directory):
            return Events(backup=backup)
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
            os.makedirs(directory)

        for task in self.dirty:
            task_file = '%s/%s.csv' % (directory, task)
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
            if self.backup and os.path.exists(task_file):
                os.rename(task_file, '%s~' % task_file)
            os.rename(temp.name, task_file)
        del self.dirty

    def tasks(self):
        """Generate a list of tasks in the database.

        :rtype: :obj:`list` of :obj:`str`
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
        if not new and task not in self.tasks():
            raise TaskNotExistError("Task %s does not exist!  Use `--new' to "
                                    'create it' % task)
        running = self.running()
        if running:
            raise TaskRunningError('Running task %s!' % running)
        self.append(Event(task, start))
        self.dirty = task

    def stop(self, message=None, force=False):
        """Stop running event.

        :param str message: Message to attach to event
        :param bool force: Re-stop a previously stopped event
        :raise TaskNotRunningError: No task running!

        """
        if not force and not self.running():
            raise TaskNotRunningError('No task running!')
        self.last().stop(message, force)
        self.dirty = self.last().task

    def filter(self, filt):
        """Apply filter to events.

        :param func filt: Function to filter with
        :rtype: :obj:`Events`
        :return: Events matching given filter function

        """
        return Events(filter(filt, self))

    def for_task(self, task):
        """Filter events for a specific task.

        :param str task: Task name to filter on
        :rtype: :obj:`Events`
        :return: Events marked with given task name

        """
        return self.filter(lambda x: x.task == task)

    def for_date(self, year, month=None, day=None):
        """Filter events for a specific date.

        :param int year: Year to filter on
        :param int month: Month to filter on, or :obj:`None`
        :param int day: Day to filter on, or :obj:`None`
        :rtype: :obj:`Events`
        :return: Events occurring within specified date

        """
        events = self.filter(lambda x: x.start.year == year)
        if month:
            events = events.filter(lambda x: x.start.month == month)
        if day:
            events = events.filter(lambda x: x.start.day == day)
        return events

    def for_week(self, year, week):
        """Filter events for a specific ISO-8601 week.

        :param int year: Year to filter events on
        :param int week: ISO-8601 month number to filter events on
        :rtype: :obj:`Events`
        :return: Events occurring in given ISO-8601 week

        """
        start, end = utils.iso_week_to_date(year, week)
        return self.filter(lambda x: start <= x.start.date() < end)

    def sum(self):
        """Sum duration of all events.

        :rtype: :obj:`datetime.timedelta`
        :return: Sum of all event deltas

        """
        return sum(map(operator.attrgetter('delta'), self),
                   datetime.timedelta(0))

    @staticmethod
    @contextlib.contextmanager
    def context(directory, backup=True):
        """Convenience context handler to manage reading and writing database.

        :param str directory: Database location
        :param bool backup: Whether to create backup files

        """
        events = Events.read(directory, backup)
        yield events
        if events.dirty:
            events.write(directory)
