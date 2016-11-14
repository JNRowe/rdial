#
# coding=utf-8
"""utils - Utility functions for rdial."""
# Copyright © 2012-2016  James Rowe <jnrowe@gmail.com>
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

import datetime
import functools
import os
import subprocess

import ciso8601
import click
import configobj

try:
    import cduration
except ImportError:
    cduration = None

from . import compat


# Set up informational message functions
def _colourise(text, colour):
    """Colour text, if possible.

    See also:
        :func:`click.termui.secho`

    Args:
        text (str): Text to colourise
        colour (str): Colour to display text in

    """
    click.termui.secho(text, fg=colour, bold=True)


def success(text):
    """Pretty print a success message.

    Args:
        text (str): Text to format

    """
    _colourise(text, 'green')


def fail(text):
    """Pretty print a failure message.

    Args:
        text (str): Text to format

    """
    _colourise(_('Error: %s') % (text, ), 'red')


def warn(text):
    """Pretty print a warning message.

    Args:
        text (str): Text to format

    """
    _colourise(_('Warning: %s') % (text, ), 'yellow')


def safer_repr(obj):
    """Produce a repr string for an object.

    .. note::
        This exists solely for use on deep objects that can be expelled deep in
        the dependency libraries.  It should *not* be required for any
        serviceable objects.

    Args:
        obj (object): Object to produce repr for

    Returns:
        str: :func:`repr` output, or a fallback string

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

    See also:
        :obj:`dict`

    """

    def __contains__(self, key):
        """Check for item membership.

        Args:
            key (object): Key to test for

        Returns:
            bool: True, if item in dictionary

        """
        return hasattr(self, key) or super(AttrDict, self).__contains__(key)

    def __getattr__(self, key):
        """Support item access via dot notation.

        Args:
            key (object): Key to fetch

        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError(safer_repr(key))

    def __setattr__(self, key, value):
        """Support item assignment via dot notation.

        Args:
            key (object): Key to set value for
            value (object): Value to set key to

        """
        try:
            self[key] = value
        except:
            raise AttributeError(safer_repr(key))

    def __delattr__(self, key):
        """Support item deletion via dot notation.

        Args:
            key (object): Key to delete

        """
        try:
            del self[key]
        except KeyError:
            raise AttributeError(safer_repr(key))


#: Map duration string keys to timedelta args
_MAPPER = {'D': 'days', 'H': 'hours', 'M': 'minutes', 'S': 'seconds'}


def parse_delta(string):
    """Parse ISO-8601 duration string.

    Args:
        string (str): Duration string to parse

    Returns:
        datetime.timedelta: Parsed delta object
    """
    if not string:
        return datetime.timedelta(0)
    if cduration:
        return cduration.parse_duration(string)
    parsed = {}
    block = []
    for c in string[1:]:
        if c.isalpha():
            if block:
                parsed[_MAPPER[c]] = int(''.join(block))
            block = []
        else:
            block.append(c)
    return datetime.timedelta(**parsed)  # pylint: disable=star-args


def format_delta(timedelta_):
    """Format ISO-8601 duration string.

    Args:
        timedelta_ (datetime.timedelta): Duration to process

    Returns:
        str: ISO-8601 representation of duration
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

    Args:
        string (str): Datetime string to parse

    Returns:
        datetime.datetime: Parsed datetime object

    """
    if not string:
        datetime_ = datetime.datetime.utcnow()
    else:
        datetime_ = ciso8601.parse_datetime(string[:19])
        if not datetime_:
            raise ValueError('Unable to parse timestamp %r'
                             % (safer_repr(string), ))
    return datetime_


def parse_datetime_user(string):
    """Parse datetime string from user.

    We accept the normal ISO-8601 formats, but kick through to the formats
    supported by the system's date command if parsing fails.

    Args:
        string (str): Datetime string to parse

    Returns:
        datetime.datetime: Parsed datetime object

    """
    try:
        datetime_ = parse_datetime(string)
    except ValueError:
        try:
            output = check_output(['date', '--utc', '--iso-8601=seconds', '-d',
                                   string])
            datetime_ = ciso8601.parse_datetime(output.strip()[:19])
        except subprocess.CalledProcessError:
            datetime_ = None
    if not datetime_:
        raise ValueError('Unable to parse timestamp %r'
                         % (safer_repr(string), ))
    return datetime_


def format_datetime(datetime_):
    """Format ISO-8601 datetime string.

    Args:
        datetime_ (datetime.datetime): Datetime to process

    Returns:
        str: ISO-8601 compatible string
    """
    return datetime_.strftime('%Y-%m-%dT%H:%M:%SZ')


def iso_week_to_date(year, week):
    """Generate date range for a given ISO-8601 week.

    ISO-8601 defines a week as Monday to Sunday, with the first week of a year
    being the first week containing a Thursday.

    Args:
        year (int): Year to process
        week (int): Week number to process

    Returns:
        tuple of datetime.date: Date range objects for given week
    """
    bound = datetime.date(year, 1, 4)
    iso_start = bound - datetime.timedelta(days=bound.isocalendar()[2] - 1)
    start = iso_start + datetime.timedelta(weeks=week - 1)
    end = start + datetime.timedelta(weeks=1)
    return start, end


def check_output(args, **kwargs):
    """Simple check_output implementation for Python 2.6 compatibility.

    Note:
        This hides stderr, unlike the normal check_output function.

    Args:
        args (list): Command and arguments to call

    Returns:
        str: Command output

    Raises:
        subprocess.CalledProcessError: If command execution fails
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

    Args:
        user_config (str): User defined config file
        cli_options (dict): Command line options

    Returns:
        configobj.ConfigObj: Parsed configuration data

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

    if cli_options:
        cli_conf = ['[rdial]', ]
        cli_conf.extend('%s = %r' % (k, v) for k, v in cli_options.items()
                        if v is not None)
        conf.merge(configobj.ConfigObj(cli_conf))

    return conf


def write_current(fun):
    """Decorator to write :file:`current` file on function exit.

    See also:
        :doc:`/taskbars`

    Returns:
        types.FunctionType: Wrapped function
    """
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Write value of ``task`` argument to ``current on exit.

        Args:
            args (tuple): Positional arguments
            kwargs (dict): Keyword arguments

        """
        globs = args[0]
        fun(*args, **kwargs)
        with click.open_file('%s/.current' % globs.directory, 'w') as f:
            f.write(kwargs['task'])
    return wrapper


def remove_current(fun):
    """Decorator to remove :file:`current` file on function exit.

    See also:
        :doc:`/taskbars`

    Returns:
        types.FunctionType: Wrapped function
    """
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Remove ``current`` file on exit.

        Args:
            args (tuple): Positional arguments
            kwargs (dict): Keyword arguments

        """
        globs = args[0]
        fun(*args, **kwargs)
        if os.path.isfile('%s/.current' % globs.directory):
            os.unlink('%s/.current' % globs.directory)
    return wrapper


def newer(fname, reference):
    """Check whether given file is newer than reference file.

    Args:
        fname (str): File to check
        reference (str): file to test against

    Returns:
        bool: True if ``fname`` is newer than ``reference``

    """
    return os.stat(fname).st_mtime > os.stat(reference).st_mtime


def _xdg_basedir_dir(dtype):
    """Return a user directory honouring XDG basedir spec.

    Args:
        dtype (str): Directory type to find

    Returns:
        str: Location of directory

    """
    if dtype not in ['cache', 'config', 'data']:
        return ValueError(_('Invalid directory type %r') % dtype)
    user_dir = os.getenv('XDG_%s_HOME' % dtype.upper())
    if not user_dir:
        if dtype == 'data':
            default = '.local/share'
        else:
            default = '.%s' % dtype
        user_dir = os.path.join(os.getenv('HOME', '/'), default)
    return os.path.join(user_dir, 'rdial')


def xdg_cache_location():
    """Return a cache location honouring $XDG_CACHE_HOME.

    Returns:
        str: Location of cache directory

    """
    return _xdg_basedir_dir('cache')


def xdg_config_location():
    """Return a config location honouring $XDG_CONFIG_HOME.

    .. note::
        :mod:`click` provides :func:`click.get_app_dir`, but it isn't quite XDG
        basedir compliant.  It also has no support for cache or data storage
        locations, so we need to implement these anyway.  It does however
        support Windows, which this most definitely does not.

    Returns:
        str: Location of config directory

    """
    return _xdg_basedir_dir('config')


def xdg_data_location():
    """Return a data location honouring $XDG_DATA_HOME.

    Returns:
        str: Location of data directory

    """
    return _xdg_basedir_dir('data')
