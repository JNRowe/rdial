#
# coding=utf-8
"""utils - Utility functions for rdial"""
# Copyright © 2012  James Rowe <jnrowe@gmail.com>
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

import datetime
import os
import sys

import blessings
import isodate

T = blessings.Terminal()


# Set up informational message functions
def _colourise(text, colour):
    """Colour text, if possible.

    :param str text: Text to colourise
    :param str colour: Colour to display text in
    :rtype: ``str``
    :return: Colourised text, if possible

    """
    return getattr(T, colour.replace(' ', '_'))(text)


def success(text):
    """Output a success message.

    :param str text:  Text to format
    :rtype: ``str`
    :return: Bright green text, if possible

    """
    return _colourise(text, 'bright green')


def fail(text):
    """Output a failure message.

    :param str text:  Text to format
    :rtype: ``str`
    :return: Bright red text, if possible

    """
    return _colourise(text, 'bright red')


def warn(text):
    """Output a warning message.

    :param str text:  Text to format
    :rtype: ``str`
    :return: Bright yellow text, if possible

    """
    return _colourise(text, 'bright yellow')


class RdialError(ValueError):

    """Generic exception for rdial."""

    if sys.version_info[0] == 3:
        @property
        def message(self):
            """Compatibility hack for Python 3"""
            return self.args[0]


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
