#
# coding=utf-8
"""utils - Utility functions for rdial."""
# Copyright © 2011-2015  James Rowe <jnrowe@gmail.com>
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


def safer_repr(obj):
    """Produce a repr string for an object

    .. note::
        This exists solely for use on deep objects that can be expelled deep in
        the dependency libraries.  It should *not* be required for any
        serviceable objects.

    :param object obj: Object to produce repr for
    :rtype: str
    :return: `repr` output, or a fallback string
    """
    try:
        return repr(obj)
    except Exception:
        return '<invalid repr>'


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
        """Check for item membership.

        :param object key: Key to test for
        :rtype: :obj:`bool`
        """
        return hasattr(self, key) or super(AttrDict, self).__contains__(key)

    def __getattr__(self, key):
        """Support item access via dot notation.

        :param object key: Key to fetch
        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError(safer_repr(key))

    def __setattr__(self, key, value):
        """Support item assignment via dot notation.

        :param object key: Key to set value for
        :param object value: Value to set key to
        """
        try:
            self[key] = value
        except:
            raise AttributeError(safer_repr(key))

    def __delattr__(self, key):
        """Support item deletion via dot notation.

        :param object key: Key to delete
        """
        try:
            del self[key]
        except KeyError:
            raise AttributeError(safer_repr(key))


class UTC(datetime.tzinfo):

    """UTC timezone object."""

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: :obj:`str`
        :return: Timezone representation suitable for :func:`eval`
        """
        return '%s()' % self.__class__.__name__
        return 'UTC()'

    def utcoffset(self, _):
        """Generate offset from UTC for ``datetime`` event."""
        return datetime.timedelta(0)

    def dst(self, _):
        """Generate daylight savings time for ``datetime`` event."""
        return datetime.timedelta(0)

    def tzname(self, _):
        """Generate timezone name for ``datetime`` event."""
        return 'UTC'


def parse_delta(string):
    """Parse ISO-8601 duration string.

    :param str string: Duration string to parse
    :rtype: :obj:`datetime.timedelta`
    :return: Parsed delta object
    """
    if not string:
        return datetime.timedelta(0)
    match = re.match(r"""
        P
        ((?P<days>\d+)D)?
        T?
        ((?P<hours>\d{1,2})H)?
        ((?P<minutes>\d{1,2})M)?
        ((?P<seconds>\d{1,2})?(\.(?P<microseconds>\d+)S)?)
    """, string, re.VERBOSE)
    match_dict = dict((k, int(v) if v else 0)
                      for k, v in match.groupdict().items())
    return datetime.timedelta(**match_dict)  # pylint: disable=star-args


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
            raise ValueError('Unable to parse timestamp %r'
                             % (safer_repr(string), ))
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
            datetime.replace(tzinfo=Local)  # pylint: disable=no-member
    except ValueError:
        try:
            output = check_output(['date', '--utc', '--iso-8601=seconds', '-d',
                                   string])
            datetime_ = ciso8601.parse_datetime(output.strip())
        except subprocess.CalledProcessError:
            datetime_ = None
    if not datetime_:
        raise ValueError('Unable to parse timestamp %r'
                         % (safer_repr(string), ))
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
    return datetime.datetime.utcnow().replace(tzinfo=UTC())


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
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            raise subprocess.CalledProcessError(retcode, args[0])
    if not compat.PY2:  # pragma: Python 3
        output = output.decode()
    return output


def read_config(user_config=None, cli_options=None):
    """Read configuration data.

    :type str user_config: User defined config file
    :type dict cli_options: Command line options
    :rtype: configobj.ConfigObj
    :return: Parsed configuration data
    """
    # Only base *must* exist
    conf = configobj.ConfigObj(os.path.dirname(__file__) + '/config',
                               file_error=True)
    conf['xdg_data_location'] = xdg_data_location()
    for string in os.getenv('XDG_CONFIG_DIRS', '/etc/xdg').split(':'):
        conf.merge(configobj.ConfigObj(string + '/rdial/config'))
    conf.merge(configobj.ConfigObj(xdg_config_location() + '/config'))
    conf.merge(configobj.ConfigObj(os.path.abspath('.rdialrc')))
    conf.merge(configobj.ConfigObj(user_config))

    cli_conf = ['[rdial]', ]
    cli_conf.extend("%s = %r" % (k, v) for k, v in cli_options.items()
                    if v is not None)
    conf.merge(configobj.ConfigObj(cli_conf))

    return conf


def write_current(fun):
    """Decorator to write ``current`` file on function exit.

    :seealso: :doc:`/taskbars`

    :rtype: :obj:`function`
    """
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Write value of ``task`` argument to ``current on exit.

        :param tuple args: Positional arguments
        :param dict kwargs: Keyword arguments
        """
        globs = args[0]
        fun(*args, **kwargs)
        open('%s/.current' % globs.directory, 'w').write(kwargs['task'])
    return wrapper


def remove_current(fun):
    """Decorator to remove ``current`` file on function exit.

    :seealso: :doc:`/taskbars`

    :rtype: :obj:`function`
    """
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Remove ``current`` file on exit.

        :param tuple args: Positional arguments
        :param dict kwargs: Keyword arguments
        """
        globs = args[0]
        fun(*args, **kwargs)
        if os.path.isfile('%s/.current' % globs.directory):
            os.unlink('%s/.current' % globs.directory)
    return wrapper


def newer(fname, reference):
    """Check whether given file is newer than reference file.

    :param str fname: File to check
    :param str reference: file to test against
    :rtype: :obj:`bool`
    :return: True if ``fname`` is newer than ``reference``
    """
    return os.stat(fname).st_mtime > os.stat(reference).st_mtime


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
