#
"""events - Event models for rdial."""
# Copyright © 2011-2019  James Rowe <jnrowe@gmail.com>
#                        Nathan McGregor <nathan.mcgregor@astrium.eads.net>
#
# SPDX-License-Identifier: GPL-3.0+
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

import contextlib
import csv
import datetime
import glob
import inspect
import operator
import os
import pickle
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Union

import click

from jnrbase import iso_8601, xdg_basedir

try:
    import cduration
except ImportError:  # pragma: no cover
    cduration = None

from . import utils


class RdialDialect(csv.unix_dialect):  # pylint: disable=too-few-public-methods
    """CSV dialect for rdial data files."""

    quoting = csv.QUOTE_MINIMAL
    strict = True


class TaskNotRunningError(utils.RdialError):
    """Exception for calling mutators when a task is not running."""


class TaskRunningError(utils.RdialError):
    """Exception for starting task when a task is already running."""


class TaskNotExistError(utils.RdialError):
    """Exception for attempting to operate on a non-existing task."""


class Event:
    """Base object for handling database event."""

    def __init__(self,
                 __task: str,
                 start: Optional[Union[datetime.datetime, str]] = None,
                 delta: Optional[Union[datetime.timedelta, str]] = None,
                 message: Optional[str] = '') -> None:
        """Initialise a new ``Event`` object.

        Args:
            __task: Task name to track
            start: Start time for event
            delta: Duration for event
            message: Message to attach to event

        """
        self.task = __task
        if isinstance(start, datetime.datetime):
            if start.tzinfo:
                raise ValueError(f'Must be a naive datetime {start!r}')
            self.start = start
        else:
            self.start = iso_8601.parse_datetime(start).replace(tzinfo=None)
        if isinstance(delta, datetime.timedelta):
            self.delta = delta
        else:
            if cduration:
                if delta:
                    self.delta = cduration.parse_duration(delta)
                else:
                    self.delta = datetime.timedelta(0)
            else:
                self.delta = iso_8601.parse_delta(delta)
        self.message = message

    def __eq__(self, __other: 'Event') -> bool:
        """Comare ``Event`` objects for equality.

        Args:
            __other: Object to test equality against

        Returns:
            True if objects are equal
        """
        return self.task == __other.task and self.start == __other.start \
            and self.delta == __other.delta and self.message == __other.message

    def __ne__(self, __other: 'Event') -> bool:
        """Comare ``Event`` objects for inequality.

        Args:
            __other: Object to test inequality against

        Returns:
            True if objects are not equal
        """
        return not self == __other

    def __repr__(self) -> str:
        """Self-documenting string representation.

        Returns:
            Event representation suitable for :func:`eval`
        """
        return 'Event({!r}, {!r}, {!r}, {!r})'.format(
            self.task,
            iso_8601.format_datetime(self.start) + 'Z',
            iso_8601.format_delta(self.delta), self.message)

    def writer(self) -> Dict[str, Optional[str]]:
        """Prepare object for export.

        Returns:
            Event data for object storage

        """
        return {
            'start': iso_8601.format_datetime(self.start) + 'Z',
            'delta': iso_8601.format_delta(self.delta),
            'message': self.message,
        }

    def running(self) -> Union[str, bool]:
        """Check if event is running.

        Returns:
            Event name, if running

        """
        if self.delta == datetime.timedelta(0):
            return self.task
        return False

    def stop(self, message: Optional[str] = None, force: bool = False) -> None:
        """Stop running event.

        Args:
            message: Message to attach to event
            force: Re-stop a previously stopped event

        Raises:
            TaskNotRunningError: Event not running

        """
        if not force and self.delta:
            raise TaskNotRunningError('No task running!')
        self.delta = datetime.datetime.utcnow() - self.start
        self.message = message


FIELDS = list(inspect.signature(Event).parameters.keys())[1:]  # NOQA


class Events(list):  # pylint: disable=too-many-public-methods
    """Container for database events."""

    def __init__(self,
                 __iterable: Optional[List[Event]] = None,
                 backup: bool = True) -> None:
        """Initialise a new ``Events`` object.

        Args:
            __iterable: Objects to add to container
            backup: Whether to create backup files

        """
        super(Events, self).__init__(__iterable if __iterable else [])
        self.backup = backup
        self._dirty = set()

    def __repr__(self) -> str:
        """Self-documenting string representation.

        Returns:
            Events representation suitable for :func:`eval`
        """
        return 'Events({})'.format(super(self.__class__, self).__repr__())

    @property
    def dirty(self) -> Iterable[str]:
        """Modified tasks requiring sync against storage."""
        return self._dirty

    @dirty.setter
    def dirty(self, __value: str):
        """Mark task as needing sync.

        Args:
            __value: Task to mark as dirty

        """
        self._dirty.add(__value)

    @dirty.deleter
    def dirty(self):
        """Mark dirty queue as flushed."""
        self._dirty = set()

    @staticmethod
    def read(__directory: str, backup: bool = True,
             write_cache: bool = True) -> 'Events':
        """Read and parse database.

        .. note::

            Assumes a new :obj:`Events` object should be created if the
            directory is missing.

        Args:
            __directory: Location to read database files from
            backup: Whether to create backup files
            write_cache: Whether to write cache files

        Returns:
            Parsed events database

        """
        if not os.path.exists(__directory):
            return Events(backup=backup)
        events = []
        xdg_cache_dir = xdg_basedir.user_cache('rdial')
        cache_dir = os.path.join(xdg_cache_dir, __directory.replace('/', '_'))
        if write_cache and not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)
            with click.open_file(f'{xdg_cache_dir}/CACHEDIR.TAG', 'w') as f:
                f.writelines([
                    'Signature: 8a477f597d28d172789f06886806bc55\n',
                    '# This file is a cache directory tag created by rdial.\n',
                    '# For information about cache directory tags, see:\n',
                    '#   http://www.brynosaurus.com/cachedir/\n',
                ])
        for fname in glob.glob(f'{__directory}/*.csv'):
            task = os.path.basename(fname)[:-4]
            cache_file = os.path.join(cache_dir, task) + '.pkl'
            evs = None
            if os.path.exists(cache_file) and utils.newer(cache_file, fname):
                try:
                    # UnicodeDecodeError must be caught for the Python 2 to
                    # 3 upgrade path.
                    with click.open_file(cache_file, 'rb') as f:
                        cache = pickle.load(f)
                except (pickle.UnpicklingError, EOFError, ImportError,
                        UnicodeDecodeError):
                    pass
                else:
                    if isinstance(cache, dict) and cache['version'] == 1:
                        evs = cache['events']
                    else:
                        os.unlink(cache_file)
            if evs is None:
                with click.open_file(fname, encoding='utf-8') as f:
                    # We're not using the prettier DictReader here as it is
                    # *significantly* slower for large data files (~5x).
                    reader = csv.reader(f, dialect=RdialDialect)
                    if not next(reader) == FIELDS:
                        raise ValueError('Invalid data {!r}'.format(
                            click.format_filename(fname)))
                    evs = [
                        Event(task, *row)  # pylint: disable=star-args
                        for row in reader
                    ]
                if write_cache:
                    with click.open_file(cache_file, 'wb', atomic=True) as f:
                        pickle.dump({
                            'version': 1,
                            'events': evs
                        }, f, pickle.HIGHEST_PROTOCOL)
            events.extend(evs)
        return Events(sorted(events, key=operator.attrgetter('start')))

    def write(self, __directory: str) -> None:
        """Write database file.

        Args:
            __directory: Location to write database files to

        """
        if not self.dirty:
            return
        if not os.path.isdir(__directory):
            os.makedirs(__directory)

        for task in self.dirty:
            task_file = f'{__directory}/{task}.csv'
            events = self.for_task(task)
            with click.utils.LazyFile(task_file, 'w', atomic=True) as temp:
                writer = csv.DictWriter(temp, FIELDS, dialect=RdialDialect)
                writer.writeheader()
                for event in events:
                    writer.writerow(event.writer())
                if self.backup and os.path.exists(task_file):
                    os.rename(task_file, f'{task_file}~')
        del self.dirty

    def tasks(self) -> List[str]:
        """Generate a list of tasks in the database.

        Returns:
            Names of tasks in database

        """
        return sorted({event.task for event in self})

    def last(self) -> Optional[Event]:
        """Return current/last event.

        .. note::

            This handles the empty database case by returning ``None``.

        Returns:
            Last recorded event

        """
        if len(self) > 0:
            return self[-1]
        else:
            return None

    def running(self) -> Union[str, bool]:
        """Check if an event is running.

        We return the running task, if one exists, for easy access.

        Returns:
            Running event, if an event running

        """
        last = self.last()
        return last.running() if last else False

    def start(self,
              __task: str,
              new: bool = False,
              start: Union[datetime.datetime, str] = '') -> None:
        """Start a new event.

        Args:
            __task: Task name to track
            new: Whether to create a new task
            start: |ISO|-8601 start time for event

        Raises:
            TaskRunningError: An event is already running

        """
        if not new and __task not in self.tasks():
            raise TaskNotExistError(
                f'Task {__task} does not exist!  Use “--new” to create it')
        running = self.running()
        if running:
            raise TaskRunningError(f'Running task {running}!')
        last = self.last()
        if last and start and last.start + last.delta > start:
            raise TaskRunningError('Start date overlaps previous task!')
        self.append(Event(__task, start))
        self.dirty = __task

    def stop(self, message: Optional[str] = None, force: bool = False) -> None:
        """Stop running event.

        Args:
            message: Message to attach to event
            force: Re-stop a previously stopped event

        Raises:
            TaskNotRunningError: No task running!

        """
        if not force and not self.running():
            raise TaskNotRunningError('No task running!')
        self.last().stop(message, force)
        self.dirty = self.last().task

    def filter(self, __filt: Callable[[
            Event,
    ], bool]) -> 'Events':
        """Apply filter to events.

        Args:
            __filt: Function to filter with

        Returns:
            Events matching given filter function

        """
        return Events(x for x in self if __filt(x))

    def for_task(self, __task: str) -> 'Events':
        """Filter events for a specific task.

        Args:
            __task: Task name to filter on

        Returns:
            Events marked with given task name

        """
        return self.filter(lambda x: x.task == __task)

    def for_date(self,
                 year: int,
                 month: Optional[int] = None,
                 day: Optional[int] = None) -> 'Events':
        """Filter events for a specific date.

        Args:
            year: Year to filter on
            month: Month to filter on
            day: Day to filter on

        Returns:
            Events occurring within specified date

        """
        events = self.filter(lambda x: x.start.year == year)
        if month:
            events = events.filter(lambda x: x.start.month == month)
        if day:
            events = events.filter(lambda x: x.start.day == day)
        return events

    def for_week(self, __year: int, __week: int) -> 'Events':
        """Filter events for a specific |ISO|-8601 week.

        Args:
            __year: Year to filter events on
            __week: |ISO|-8601 week number to filter events on

        Returns:
            Events occurring in given |ISO|-8601 week
        """
        start, end = utils.iso_week_to_date(__year, __week)
        return self.filter(lambda x: start <= x.start.date() < end)

    def sum(self) -> datetime.timedelta:
        """Sum duration of all events.

        Returns:
            Sum of all event deltas

        """
        return sum((x.delta for x in self), datetime.timedelta(0))

    @staticmethod
    @contextlib.contextmanager
    def wrapping(__directory: str,
                 backup: bool = True,
                 write_cache: bool = True) -> Iterator['Events']:
        """Convenience context handler to manage reading and writing database.

        Args:
            __directory: Database location
            backup: Whether to create backup files
            write_cache: Whether to write cache files

        """
        events = Events.read(__directory, backup, write_cache)
        yield events
        if events.dirty:
            events.write(__directory)
