#! /usr/bin/env python -tt

import datetime


class UTC(datetime.tzinfo):  # pragma: nocover
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'


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
