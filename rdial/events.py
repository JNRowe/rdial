#
# coding=utf-8
"""events - Event models for rdial."""
# Copyright © 2011-2016  James Rowe <jnrowe@gmail.com>
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

from __future__ import absolute_import

import contextlib
import datetime
import glob
import inspect
import operator
import os

try:
    import cPickle as pickle
except ImportError:  # Python 3, and 2.x without speedy helper
    import pickle  # NOQA

import click

from . import compat
from . import utils

if compat.PY2:
    import unicodecsv as csv
else:
    import csv


class RdialDialect(csv.excel):  # pylint: disable=too-few-public-methods

    """CSV dialect for rdial data files."""

    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL
    strict = True


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

        Args:
            task (str): Task name to tracking
            start (datetime.datetime): Start time for event
            delta (datetime.timedelta): Duration for event
            message (str): Message to attach to event
        """
        self.task = task
        if isinstance(start, datetime.datetime):
            if start.tzinfo:
                raise ValueError('Must be a naive datetime %r' %
                                 (utils.safer_repr(start), ))
            self.start = start
        else:
            self.start = utils.parse_datetime(start)
        if isinstance(delta, datetime.timedelta):
            self.delta = delta
        else:
            self.delta = utils.parse_delta(delta)
        self.message = message

    @compat.mangle_repr_type
    def __repr__(self):
        """Self-documenting string representation.

        Returns:
            str: Event representation suitable for :func:`eval`
        """
        return 'Event(%r, %r, %r, %r)' \
            % (self.task, utils.format_datetime(self.start),
               utils.format_delta(self.delta), self.message)

    def writer(self):
        """Prepare object for export.

        Returns:
            dict: Event data for object storage
        """
        return {
            'start': utils.format_datetime(self.start),
            'delta': utils.format_delta(self.delta),
            'message': self.message,
        }

    def running(self):
        """Check if event is running.

        Returns:
            str: Event name, if running
        """
        if self.delta == datetime.timedelta(0):
            return self.task
        return False

    def stop(self, message=None, force=False):
        """Stop running event.

        Args:
            message (str): Message to attach to event
            force (bool): Re-stop a previously stopped event

        Raises:
            TaskNotRunningError: Event not running
        """
        if not force and self.delta:
            raise TaskNotRunningError('No task running!')
        self.delta = datetime.datetime.utcnow() - self.start
        self.message = message
FIELDS = inspect.getargspec(Event.__init__)[0][2:]


class Events(list):  # pylint: disable=too-many-public-methods

    """Container for database events."""

    def __init__(self, iterable=None, backup=True):
        """Initialise a new ``Events`` object.

        Args:
            iterable (list): Objects to add to container
            backup (bool): Whether to create backup files
        """
        super(Events, self).__init__(iterable if iterable else [])
        self.backup = backup
        self._dirty = []

    @compat.mangle_repr_type
    def __repr__(self):
        """Self-documenting string representation.

        Returns:
            str: Events representation suitable for :func:`eval`
        """
        return 'Events(%s)' % super(self.__class__, self).__repr__()

    @property
    def dirty(self):
        """Modified tasks requiring sync against storage."""
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        """Mark task as needing sync.

        Args:
            value (str): Task to mark as dirty
        """
        if value not in self._dirty:
            self._dirty.append(value)

    @dirty.deleter
    def dirty(self):
        """Mark dirty queue as flushed."""
        self._dirty = []

    @staticmethod
    def read(directory, backup=True, write_cache=True):
        """Read and parse database.

        Assume a new :obj:`Events` object should be created if the file is
        missing

        Args:
            directory (str): Location to read database files from
            backup (bool): Whether to create backup files
            write_cache (bool): Whether to write cache files

        Returns:
            Events: Parsed events database
        """
        if not os.path.exists(directory):
            return Events(backup=backup)
        events = []
        xdg_cache_dir = utils.xdg_cache_location()
        cache_dir = os.path.join(xdg_cache_dir, directory.replace('/', '_'))
        if write_cache and not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)
            with open('%s/CACHEDIR.TAG' % xdg_cache_dir, 'w') as f:
                f.writelines([
                    'Signature: 8a477f597d28d172789f06886806bc55\n',
                    '# This file is a cache directory tag created by rdial.\n',
                    '# For information about cache directory tags, see:\n',
                    '#   http://www.brynosaurus.com/cachedir/\n',
                ])
        for fname in glob.glob('%s/*.csv' % directory):
            task = os.path.basename(fname)[:-4]
            cache_file = os.path.join(cache_dir, task) + '.pkl'
            evs = None
            if os.path.exists(cache_file) and utils.newer(cache_file, fname):
                try:
                    with click.open_file(cache_file, 'rb') as f:
                        cache = pickle.load(f)
                except (pickle.UnpicklingError, ImportError):
                    pass
                else:
                    try:
                        assert cache['version'] == 1
                    except TypeError:
                        os.unlink(cache_file)
                    else:
                        evs = cache['events']
            if evs is None:
                with click.open_file(fname, encoding='utf-8') as f:
                    # We're not using the prettier DictReader here as it is
                    # *significantly* slower for large data files (~5x).
                    reader = csv.reader(f, dialect=RdialDialect)
                    assert next(reader) == FIELDS, 'Invalid data %r' % fname
                    evs = [Event(task, *row)  # pylint: disable=star-args
                           for row in reader]
                if write_cache:
                    with click.open_file(cache_file, 'wb', atomic=True) as f:
                        pickle.dump({'version': 1, 'events': evs}, f,
                                    pickle.HIGHEST_PROTOCOL)
            events.extend(evs)
        return Events(sorted(events, key=operator.attrgetter('start')))

    def write(self, directory):
        """Write database file.

        Args:
            directory (str): Location to write database files to
        """
        if not self.dirty:
            return
        if not os.path.isdir(directory):
            os.makedirs(directory)

        for task in self.dirty:
            task_file = '%s/%s.csv' % (directory, task)
            events = self.for_task(task)
            with click.utils.LazyFile(task_file, 'w', atomic=True) as temp:
                writer = csv.DictWriter(temp, FIELDS, dialect=RdialDialect)
                # Can't use writeheader, it wasn't added until 2.7.
                writer.writerow(dict(zip(FIELDS, FIELDS)))
                for event in events:
                    writer.writerow(event.writer())
                if self.backup and os.path.exists(task_file):
                    os.rename(task_file, '%s~' % task_file)
        del self.dirty

    def tasks(self):
        """Generate a list of tasks in the database.

        Returns:
            list of str: Names of tasks in database
        """
        return sorted(set(event.task for event in self))

    def last(self):
        """Return current/last event.

        This handles the empty database case by returning ``None``

        Returns:
            Event: Last recorded event
        """
        if len(self) > 0:
            return self[-1]
        else:
            return None

    def running(self):
        """Check if an event is running.

        We return the running task, if one exists, for easy access.

        Returns:
            Event: Running event, if an event running
        """
        last = self.last()
        return last.running() if last else False

    def start(self, task, new=False, start=''):
        """Start a new event.

        Args:
            task (str): Task name to tracking
            start (str): ISO-8601 start time for event

        Raises:
            TaskRunningError: An event is already running
        """
        if not new and task not in self.tasks():
            raise TaskNotExistError("Task %s does not exist!  Use `--new' to "
                                    'create it' % task)
        running = self.running()
        if running:
            raise TaskRunningError('Running task %s!' % running)
        last = self.last()
        if last and start and last.start + last.delta > start:
            raise TaskRunningError('Start date overlaps previous task!')
        self.append(Event(task, start))
        self.dirty = task

    def stop(self, message=None, force=False):
        """Stop running event.

        Args:
            message (str): Message to attach to event
            force (bool): Re-stop a previously stopped event

        Raises:
            TaskNotRunningError: No task running!
        """
        if not force and not self.running():
            raise TaskNotRunningError('No task running!')
        self.last().stop(message, force)
        self.dirty = self.last().task

    def filter(self, filt):
        """Apply filter to events.

        Args:
            filt (types.FunctionType): Function to filter with

        Returns:
            Events: Events matching given filter function
        """
        return Events(x for x in self if filt(x))

    def for_task(self, task):
        """Filter events for a specific task.

        Args:
            task (str): Task name to filter on

        Returns:
            Events: Events marked with given task name
        """
        return self.filter(lambda x: x.task == task)

    def for_date(self, year, month=None, day=None):
        """Filter events for a specific date.

        Args:
            year (int): Year to filter on
            month (int): Month to filter on, or :obj:`None`
            day (int): Day to filter on, or :obj:`None`

        Returns:
            Events: Events occurring within specified date
        """
        events = self.filter(lambda x: x.start.year == year)
        if month:
            events = events.filter(lambda x: x.start.month == month)
        if day:
            events = events.filter(lambda x: x.start.day == day)
        return events

    def for_week(self, year, week):
        """Filter events for a specific ISO-8601 week.

        Args:
            year (int): Year to filter events on
            week (int): ISO-8601 month number to filter events on

        Returns:
            Events: Events occurring in given ISO-8601 week
        """
        start, end = utils.iso_week_to_date(year, week)
        return self.filter(lambda x: start <= x.start.date() < end)

    def sum(self):
        """Sum duration of all events.

        Returns:
            datetime.timedelta: Sum of all event deltas
        """
        return sum((x.delta for x in self), datetime.timedelta(0))

    @staticmethod
    @contextlib.contextmanager
    def context(directory, backup=True, write_cache=True):
        """Convenience context handler to manage reading and writing database.

        Args:
            directory (str): Database location
            backup (bool): Whether to create backup files
            write_cache (bool): Whether to write cache files
        """
        events = Events.read(directory, backup, write_cache)
        yield events
        if events.dirty:
            events.write(directory)
