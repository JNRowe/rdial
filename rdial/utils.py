#
# coding=utf-8
"""utils - Utility functions for rdial."""
# Copyright © 2012-2017  James Rowe <jnrowe@gmail.com>
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

from jnrbase import (compat, xdg_basedir)
from jnrbase.iso_8601 import parse_datetime


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


#: Map duration string keys to timedelta args
_MAPPER = {'D': 'days', 'H': 'hours', 'M': 'minutes', 'S': 'seconds'}


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
        datetime_ = parse_datetime(string).replace(tzinfo=None)
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
    conf['xdg_data_location'] = xdg_basedir.user_data('rdial')
    for f in xdg_basedir.get_configs('rdial'):
        conf.merge(configobj.ConfigObj(f))
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


def term_link(target, name=None):
    """Generate a terminal hyperlink

    See https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda.

    Args:
        target (str): Hyperlink target
        name (str): Target name

    Returns:
        str: Formatted hyperlink for terminal output
    """
    if not name:
        name = os.path.basename(target)
    return '\033]8;;%s\007%s\033]8;;\007' % (target, name)
