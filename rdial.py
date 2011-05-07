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
import re


class UTC(datetime.tzinfo):
    """UTC timezone object"""
    def __repr__(self):
        return 'UTC()'

    # pylint: disable-msg=W0613
    def utcoffset(self, datetime_):
        return datetime.timedelta(0)

    def dst(self, datetime_):
        return datetime.timedelta(0)

    def tzname(self, datetime_):
        return 'UTC'
    # pylint: enable-msg=W0613


class Event(object):
    """Base object for handling database event"""
    def __init__(self, project, start="", delta=""):
        """Initialise a new ``Event`` object

        :param str project: Project name to tracking
        :param str start: ISO-8601 start time for event
        :param str delta: ISO-8601 duration for event
        """
        self.project = project
        self.start = parse_datetime(start)
        self.delta = parse_delta(delta)

    def __repr__(self):
        """Self-documenting string representation"""
        return 'Event(%r, %r, %r)' % (self.project,
                                      format_datetime(self.start),
                                      format_delta(self.delta))

    def writer(self):
        """Prepare object for export"""
        return {
            'project': self.project,
            'start': format_datetime(self.start),
            'delta': format_delta(self.delta)
        }

    def running(self):
        """Check if event is running"""
        if self.delta == datetime.timedelta(0):
            return self.project
        return False
FIELDS = inspect.getargspec(Event.__init__).args[1:]


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


def parse_delta(string):
    """Parse ISO-8601 duration string

    :param str string: Duration string to parse
    :rtype: datetime.timedelta
    """
    if not string:
        return datetime.timedelta(0)
    match = re.match("""
        P
        ((?P<days>\d+)D)?
        T?
        ((?P<hours>\d{1,2})H)?
        ((?P<minutes>\d{1,2})M)?
        ((?P<seconds>\d{1,2})S)?
    """, string, re.VERBOSE)
    match_dict = dict((k, int(v) if v else 0)
                      for k, v in match.groupdict().items())
    return datetime.timedelta(**match_dict)  # pylint: disable-msg=W0142


def format_delta(timedelta_):
    """Format ISO-8601 duration string

    :param datetime.timedelta timedelta_: Duration to process
    :rtype: str
    """
    if timedelta_ == datetime.timedelta(0):
        return ""
    days = "%dD" % timedelta_.days if timedelta_.days else ""
    hours, minutes = divmod(timedelta_.seconds, 3600)
    minutes, seconds = divmod(minutes, 60)
    hours = "%02dH" % hours if hours else ""
    minutes = "%02dM" % minutes if minutes else ""
    seconds = "%02dS" % seconds if seconds else ""
    return 'P%s%s%s%s%s' % (days, "T" if hours or minutes or seconds else "",
                            hours, minutes, seconds)


def parse_datetime(string):
    """Parse ISO-8601 datetime string

    :param str string: Datetime string to parse
    :rtype: datetime.datetime
    """
    if string == "":
        datetime_ = datetime.datetime.utcnow()
    else:
        datetime_ = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
    return datetime_.replace(tzinfo=UTC())


def format_datetime(datetime_):
    """Format ISO-8601 datetime string

    :param datetime.datetime datetime_: Datetime to process
    :rtype: str
    """
    # Can't call isoformat method as it uses the +00:00 form
    return datetime_.strftime('%Y-%m-%dT%H:%M:%SZ')
