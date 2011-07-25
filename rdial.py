#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""rdial - Simple time tracking for simple people"""
# Copyright (C) 2011  James Rowe <jnrowe@gmail.com>
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

__version__ = "0.1.0"
__date__ = "2011-05-04"
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2011  James Rowe <jnrowe@gmail.com>"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See git repository"

from email.utils import parseaddr

__doc__ += """.

A simple time tracking tool, with no frills and no fizzy coating.

.. moduleauthor:: `%s <mailto:%s>`__
""" % parseaddr(__author__)

import csv
import datetime
import inspect
import os

import argh
import isodate


class Event(object):
    """Base object for handling database event"""
    def __init__(self, project, start="", delta="", message=""):
        """Initialise a new ``Event`` object

        :param str project: Project name to tracking
        :param str start: ISO-8601 start time for event
        :param str delta: ISO-8601 duration for event
        :param str message: Message to attach to event
        """
        self.project = project
        self.start = parse_datetime(start)
        self.delta = parse_delta(delta)
        self.message = message

    def __repr__(self):
        """Self-documenting string representation"""
        return 'Event(%r, %r, %r, %r)' \
            % (self.project, isodate.datetime_isoformat(self.start),
               format_delta(self.delta), self.message)

    def writer(self):
        """Prepare object for export"""
        return {
            'project': self.project,
            'start': isodate.datetime_isoformat(self.start),
            'delta': format_delta(self.delta),
            'message': self.message,
        }

    def running(self):
        """Check if event is running"""
        if self.delta == datetime.timedelta(0):
            return self.project
        return False

    def stop(self):
        """Stop currently running event

        :raise ValueError: Event not running
        """
        if self.delta:
            raise ValueError('Not running!')
        self.delta = utcnow() - self.start
FIELDS = inspect.getargspec(Event.__init__)[0][1:]


class Events(list):
    """Container for database events"""
    def __repr__(self):
        """Self-documenting string representation"""
        return 'Events(%s)' % super(self.__class__, self).__repr__()

    @staticmethod
    def read(filename):
        """Read and parse database

        Assume a new ``Events`` object should be created if the file is missing

        :param str filename: Database file to read
        :returns Events: Parsed events database
        """
        if not os.path.exists(filename):
            return Events()
        # pylint: disable-msg=W0142
        return Events([Event(**d)
                       for d in csv.DictReader(open(filename), FIELDS)])

    def write(self, filename):
        """Write database outline

        :param str filename: Database file to write
        """
        dir = os.path.dirname(filename)
        if not os.path.isdir(dir):
            os.mkdir(dir)

        writer = csv.DictWriter(open(filename, 'w'), FIELDS,
                                lineterminator='\n')
        for event in self:
            writer.writerow(event.writer())

    def projects(self):
        """Generate a list of projects in the database"""
        return sorted(set(event.project for event in self))

    def last(self):
        """Return current/last event

        This handles the empty database case by returning ``False``
        """
        if len(self) > 0:
            return self[-1]
        else:
            return False

    def running(self):
        """Check if an event is running"""
        last = self.last()
        return last.running() if last else False

    def start(self, project):
        """Start a new event

        :param str project: Project name to tracking
        """
        if self.running():
            raise ValueError('Currently running task!')
        self.append(Event(project))

    def stop(self):
        """Stop currently running event

        :raise ValueError: No currently running task
        """
        if not self.running():
            raise ValueError('No currently running task!')
        self.last().stop()

    def filter(self, filt):
        """Apply filter to events

        :param func filt: Function to filter with
        :rtype: Events
        """
        return Events(filter(filt, self))

    def for_project(self, project):
        """Filter events for a specific project

        :param str project: Project name to filter on
        :rtype: Events
        """
        return self.filter(lambda x: x.project == project)

    def for_year(self, year):
        """Filter events for a specific year

        :param str project: Project name to filter on
        :param int year: Year to filter on
        :rtype: Events
        """
        return self.filter(lambda x: x.start.year == year)

    def for_month(self, year, month):
        """Filter events for a specific month

        :param str project: Project name to filter on
        :param int year: Year to filter on
        :param int month: Month to filter on
        :rtype: Events
        """
        filt = lambda x: (x.start.year, x.start.month) == (year, month)
        return self.filter(filt)

    def for_day(self, year, month, day):
        """Filter events for a specific day

        :param str project: Project name to filter on
        :param int year: Year to filter on
        :param int month: Month to filter on
        :param int day: Day to filter on
        :rtype: Events
        """
        filt = lambda x: x.start.date() == datetime.date(year, month, day)
        return self.filter(filt)

    def sum(self):
        """Sum duration of all events

        :rtype: datetime.timedelta
        """
        return sum(map(lambda x: x.delta, self), datetime.timedelta(0))


def parse_delta(string):
    """Parse ISO-8601 duration string

    :param str string: Duration string to parse
    :rtype: datetime.timedelta
    """
    if not string:
        return datetime.timedelta(0)
    return isodate.parse_duration(string)


def format_delta(timedelta_):
    """Format ISO-8601 duration string

    :param datetime.timedelta timedelta_: Duration to process
    :rtype: str
    """
    if timedelta_ == datetime.timedelta(0):
        return ""
    return isodate.duration_isoformat(timedelta_)


def parse_datetime(string):
    """Parse ISO-8601 datetime string

    :param str string: Datetime string to parse
    :rtype: datetime.datetime
    """
    if string == "":
        datetime_ = utcnow()
    else:
        datetime_ = isodate.parse_datetime(string)
    return datetime_


def utcnow():
    """Wrapper for producing timezone aware current timestamp

    :rtype: datetime.datetime
    """
    return datetime.datetime.utcnow().replace(tzinfo=isodate.UTC)


def xdg_data_file(file='data'):
    """Return a data location honouring $XDG_DATA_HOME

    :param str file: Filename in data storage directory
    :rtype: str
    """
    user_dir = os.getenv('XDG_DATA_HOME', os.path.join(os.getenv('HOME', '/'),
                         '.local/share'))
    return os.path.join(user_dir, 'rdial', file)


@argh.arg('task', default='default', nargs='?', help='task name')
def start(args):
    "start task"
    events = Events.read(xdg_data_file())
    events.start(args.task)
    events.write(xdg_data_file())


def stop(args):
    "stop task"
    events = Events.read(xdg_data_file())
    events.stop()
    events.write(xdg_data_file())


@argh.arg('task', nargs='?', help='task name')
def report(args):
    "report time tracking data"
    events = Events.read(xdg_data_file())
    if args.task:
        events = events.for_project(args.task)
    yield events.sum()
    if events.running():
        current = events.last()
        yield 'Currently running %s since %s' \
            % (current.project, isodate.datetime_isoformat(current.start))


def main():
    """Main script"""
    description = __doc__.splitlines()[0].split("-", 1)[1]
    epilog = "Please report bugs to jnrowe@gmail.com"
    parser = argh.ArghParser(description=description, epilog=epilog,
                             version="%%(prog)s %s" % __version__)
    parser.add_commands([start, stop, report])
    parser.dispatch()

if __name__ == '__main__':
    main()
