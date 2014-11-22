#
# coding=utf-8
"""utils - Utility functions for rdial"""
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

import datetime
import functools
import os
import re
import subprocess

import ciso8601
import click
import configobj

from pytz.reference import Local

from . import compat


# Set up informational message functions
def _colourise(text, colour):
    """Colour text, if possible.

    :param str text: Text to colourise
    :param str colour: Colour to display text in
    """
    click.termui.secho(text, fg=colour, bold=True)


def success(text):
    """Pretty print a success message.

    :param str text: Text to format
    """
    _colourise(text, 'green')


def fail(text):
    """Pretty print a failure message.

    :param str text: Text to format
    """
    _colourise(text, 'red')


def warn(text):
    """Pretty print a warning message.

    :param str text: Text to format
    """
    _colourise(text, 'yellow')


class RdialError(ValueError):

    """Generic exception for rdial."""

    if not compat.PY2:  # pragma: Python 3
        @property
        def message(self):
            """Compatibility hack for Python 3."""
            return self.args[0]


class AttrDict(dict):

    """Dictionary with attribute access.

    .. seealso:: :obj:`dict`
    """

    def __contains__(self, key):
        """Check for item membership

        :param object key: Key to test for
        :rtype: :obj:`bool`
        """
        return hasattr(self, key) or super(AttrDict, self).__contains__(key)

    def __getattr__(self, key):
        """Support item access via dot notation

        :param object key: Key to fetch
        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        """Support item assignment via dot notation

        :param object key: Key to set value for
        :param object value: Value to set key to
        """
        try:
            self[key] = value
        except:
            raise AttributeError(key)

    def __delattr__(self, key):
        """Support item deletion via dot notation

        :param object key: Key to delete
        """
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


class UTC(datetime.tzinfo):

    """UTC timezone object."""

    def __repr__(self):
        return '%s()' % self.__class__.__name__

    # pylint: disable-msg=W0613
    def utcoffset(self, datetime_):
        return datetime.timedelta(0)

    def dst(self, datetime_):
        return datetime.timedelta(0)

    def tzname(self, datetime_):
        return 'UTC'
    # pylint: enable-msg=W0613

utc = UTC()


def parse_delta(string):
    """Parse ISO-8601 duration string.

    :param str string: Duration string to parse
    :rtype: :obj:`datetime.timedelta`
    :return: Parsed delta object
    """
    if not string:
        return datetime.timedelta(0)
    match = re.match("""
        P
        ((?P<days>\d+)D)?
        T?
        ((?P<hours>\d{1,2})H)?
        ((?P<minutes>\d{1,2})M)?
        ((?P<seconds>\d{1,2})?(\.(?P<microseconds>\d+)S)?)
    """, string, re.VERBOSE)
    match_dict = dict((k, int(v) if v else 0)
                      for k, v in match.groupdict().items())
    return datetime.timedelta(**match_dict)  # pylint: disable-msg=W0142


def format_delta(timedelta_):
    """Format ISO-8601 duration string.

    :param datetime.timedelta timedelta_: Duration to process
    :rtype: :obj:`str`
    :return: ISO-8601 representation of duration
    """
    if timedelta_ == datetime.timedelta(0):
        return ''
    days = '%dD' % timedelta_.days if timedelta_.days else ''
    hours, minutes = divmod(timedelta_.seconds, 3600)
    minutes, seconds = divmod(minutes, 60)
    hours = '%02dH' % hours if hours else ''
    minutes = '%02dM' % minutes if minutes else ''
    seconds = '%02dS' % seconds if seconds else ''
    return 'P%s%s%s%s%s' % (days, 'T' if hours or minutes or seconds else '',
                            hours, minutes, seconds)


def parse_datetime(string):
    """Parse datetime string.

    :param str string: Datetime string to parse
    :rtype: :obj:`datetime.datetime`
    :return: Parsed datetime object
    """
    if not string:
        datetime_ = utcnow()
    else:
        datetime_ = ciso8601.parse_datetime(string)
        if not datetime_:
            raise ValueError('Unable to parse timestamp %r' % string)
    return datetime_


def parse_datetime_user(string):
    """Parse datetime string from user.

    We accept the normal ISO-8601 formats, but kick through to the formats
    supported by the system's date command if parsing fails.

    :param str string: Datetime string to parse
    :rtype: :obj:`datetime.datetime`
    :return: Parsed datetime object
    """
    try:
        datetime_ = parse_datetime(string)
        if datetime_.tzinfo is None:
            datetime.replace(tzinfo=Local)
    except ValueError:
        try:
            output = check_output(['date', '--utc', '--iso-8601=seconds', '-d',
                                   string])
            datetime_ = ciso8601.parse_datetime(output.strip())
        except subprocess.CalledProcessError:
            datetime_ = None
    if not datetime_:
        raise ValueError('Unable to parse timestamp %r' % string)
    return datetime_


def format_datetime(datetime_):
    """Format ISO-8601 datetime string.

    :param datetime.datetime datetime_: Datetime to process
    :rtype: str
    :return: ISO-8601 compatible string
    """
    # Can't call isoformat method as it uses the +00:00 form
    return datetime_.strftime('%Y-%m-%dT%H:%M:%SZ')


def iso_week_to_date(year, week):
    """Generate date range for a given ISO-8601 week.

    ISO-8601 defines a week as Monday to Sunday, with the first week of a year
    being the first week containing a Thursday.

    :param int year: Year to process
    :param int week: Week number to process
    :rtype: :obj:`tuple` of :obj:`datetime.date`
    :return: Date range objects for given week
    """
    bound = datetime.date(year, 1, 4)
    iso_start = bound - datetime.timedelta(days=bound.isocalendar()[2] - 1)
    start = iso_start + datetime.timedelta(weeks=week - 1)
    end = start + datetime.timedelta(weeks=1)
    return start, end


def utcnow():
    """Wrapper for producing timezone aware current timestamp.

    :rtype: obj:`datetime.datetime`
    :return: Current date and time, in UTC

    """
    return datetime.datetime.utcnow().replace(tzinfo=utc)


def check_output(args, **kwargs):
    """Simple check_output implementation for Python 2.6 compatibility.

    ..note:: This hides stderr, unlike the normal check_output function.

    :param list args: Command and arguments to call
    :rtype: ``str``
    :return: Command output
    :raise subprocess.CalledProcessError: If command execution fails
    """
    try:
        output = subprocess.check_output(args, stderr=subprocess.PIPE,
                                         **kwargs)
    except AttributeError:
        process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            raise subprocess.CalledProcessError(retcode, args[0])
    if not compat.PY2:  # pragma: Python 3
        output = output.decode()
    return output


def read_config(user_config=None):
    """Read configuration data.

    :type str user_config: User defined config file
    :rtype: configobj.ConfigObj
    :return: Parsed configuration data
    """
    configs = [os.path.dirname(__file__) + '/config', ]
    for s in os.getenv('XDG_CONFIG_DIRS', '/etc/xdg').split(':'):
        p = s + '/rdial/config'
        if os.path.isfile(p):
            configs.append(p)
    configs.append(xdg_config_location() + '/config')
    configs.append(os.path.abspath('.rdialrc'))
    if user_config:
        configs.append(user_config)
    # Prime config with dynamic key
    lines = ['xdg_data_location = %r' % xdg_data_location(), ]
    for file in configs:
        if os.path.isfile(file):
            lines.extend(click.open_file(file, encoding='utf-8').readlines())
    return configobj.ConfigObj(lines)


def write_current(f):
    """Decorator to write ``current`` file on function exit.

    :seealso: :doc:`/taskbars`

    :rtype: :obj:`function`
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        globs = args[0]
        f(*args, **kwargs)
        open('%s/.current' % globs.directory, 'w').write(kwargs['task'])
    return wrapper


def remove_current(f):
    """Decorator to remove ``current`` file on function exit.

    :seealso: :doc:`/taskbars`

    :rtype: :obj:`function`
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        globs = args[0]
        f(*args, **kwargs)
        if os.path.isfile('%s/.current' % globs.directory):
            os.unlink('%s/.current' % globs.directory)
    return wrapper


def newer(file, reference):
    """Check whether given file is newer than reference file.

    :param str file: File to check
    :param str reference: file to test against
    :rtype: :obj:`bool`
    :return: True if ``reference`` is newer than ``reference``
    """
    return os.stat(file).st_mtime > os.stat(reference).st_mtime


def xdg_cache_location():
    """Return a cache location honouring $XDG_CACHE_HOME.

    :rtype: :obj:`str`
    """
    user_dir = os.getenv('XDG_CACHE_HOME',
                         os.path.join(os.getenv('HOME', '/'), '.cache'))
    return os.path.join(user_dir, 'rdial')


def xdg_config_location():
    """Return a config location honouring $XDG_CONFIG_HOME.

    :rtype: :obj:`str`
    """
    user_dir = os.getenv('XDG_CONFIG_HOME',
                         os.path.join(os.getenv('HOME', '/'), '.config'))
    return os.path.join(user_dir, 'rdial')


def xdg_data_location():
    """Return a data location honouring $XDG_DATA_HOME.

    :rtype: :obj:`str`
    """
    user_dir = os.getenv('XDG_DATA_HOME', os.path.join(os.getenv('HOME', '/'),
                         '.local/share'))
    return os.path.join(user_dir, 'rdial')
