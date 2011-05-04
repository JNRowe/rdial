#! /usr/bin/env python -tt

import csv
import datetime
import inspect
import re


class UTC(datetime.tzinfo):  # pragma: nocover
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'


class Event(object):
    """Base object for handling database event"""
    def __init__(self, project, start, delta=datetime.timedelta(0)):
        self.project = project
        self.start = parse_datetime(start)
        self.delta = parse_delta(delta)

    def __repr__(self):
        return 'Event(%(project)r, %(start)r, %(delta)r)' % self.__dict__
FIELDS = inspect.getargspec(Event.__init__).args[1:]


class Events(list):
    def __repr__(self):
        return 'Events(%r)' % self[:]

    @staticmethod
    def read(file):
        return Events([Event(**d) for d in csv.DictReader(open(file), FIELDS)])


def parse_delta(string):
    """Parse ISO-8601 duration string

    :param str string: Duration string to parse
    :rtype: datetime.timedelta
    """
    if not string:
        return datetime.timedelta(0)
    match = re.match("""
        PT
        ((?P<hours>\d{2})H)?
        ((?P<minutes>\d{2})M)?
        ((?P<seconds>\d{2})S)
    """, string, re.VERBOSE)
    match_dict = dict((k, int(v) if v else 0)
                      for k, v in match.groupdict().items())
    return datetime.timedelta(**match_dict)


def format_delta(timedelta_):
    """Format ISO-8601 duration string

    :param datetime.timedelta timedelta_: Duration to process
    :rtype: str
    """
    if timedelta_ == datetime.timedelta(0):
        return ""
    hours, minutes = divmod(timedelta_.seconds, 3600)
    minutes, seconds = divmod(minutes, 60)
    return 'PT%02dH%02dM%02dS' % (hours, minutes, seconds)


def parse_datetime(string):
    """Parse ISO-8601 datetime string

    :param str string: Datetime string to parse
    :rtype: datetime.datetime
    """
    datetime_ = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
    return datetime_.replace(tzinfo=UTC())


def format_datetime(datetime_):
    """Format ISO-8601 datetime string

    :param datetime.datetime datetime_: Datetime to process
    :rtype: str
    """
    # Can't call isoformat method as it uses the +00:00 form
    return datetime_.strftime('%Y-%m-%dT%H:%M:%SZ')
