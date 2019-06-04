#
"""utils - Utility functions for rdial."""
# Copyright © 2012-2019  James Rowe <jnrowe@gmail.com>
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

import configparser
import functools
import os
import subprocess
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from typing import Callable, ContextManager, Dict, Optional, Tuple, Union
try:
    from importlib import resources
except ImportError:  # pragma: no cover
    import importlib_resources as resources

import click

from jnrbase import xdg_basedir
from jnrbase.iso_8601 import parse_datetime


class RdialError(ValueError):
    """Generic exception for rdial."""


#: Map duration string keys to timedelta args
_MAPPER = {'D': 'days', 'H': 'hours', 'M': 'minutes', 'S': 'seconds'} \
    # type : Dict[str, str]


def parse_datetime_user(__string: str) -> datetime:
    """Parse datetime string from user.

    We accept the normal |ISO|-8601 formats, but kick through to the formats
    supported by the system’s :command:`date` command if parsing fails.

    Args:
        __string: Datetime string to parse

    Returns:
        Parsed datetime object

    """
    try:
        datetime_ = parse_datetime(__string)
    except ValueError:
        try:
            proc = subprocess.run(
                ['date', '--utc', '--iso-8601=seconds', '-d', __string],
                stdout=subprocess.PIPE,
                check=True)
            output = proc.stdout.decode()
            datetime_ = parse_datetime(output.strip()[:19])
        except subprocess.CalledProcessError:
            datetime_ = None
    if not datetime_:
        raise ValueError(f'Unable to parse timestamp {__string!r}')
    return datetime_.replace(tzinfo=None)


def iso_week_to_date(__year: int, __week: int) -> Tuple[date, date]:
    """Generate date range for a given |ISO|-8601 week.

    |ISO|-8601 defines a week as Monday to Sunday, with the first week of a
    year being the first week containing a Thursday.

    Args:
        __year: Year to process
        __week: Week number to process

    Returns:
        Date range objects for given week
    """
    bound = date(__year, 1, 4)
    iso_start = bound - timedelta(days=bound.isocalendar()[2] - 1)
    start = iso_start + timedelta(weeks=__week - 1)
    end = start + timedelta(weeks=1)
    return start, end


def read_config(user_config: Optional[str] = None,
                cli_options: Optional[Dict[str, Union[bool, str]]] = None
                ) -> configparser.ConfigParser:
    """Read configuration data.

    Args:
        user_config: User defined config file
        cli_options: Command line options

    Returns:
        Parsed configuration data

    """
    # Only base *must* exist
    conf = configparser.ConfigParser()
    # No, it *really* must
    conf.read_string(resources.read_text('rdial', 'config'), 'pkg config')
    conf['DEFAULT'] = {'xdg_data_location': xdg_basedir.user_data('rdial')}
    for f in xdg_basedir.get_configs('rdial'):
        conf.read(f)
    conf.read(os.path.abspath('.rdialrc'))
    if user_config:
        conf.read(user_config)

    if cli_options:
        conf.read_dict({
            'rdial': {k: v
                      for k, v in cli_options.items() if v is not None}
        })

    return conf


def write_current(__fun: Callable) -> Callable:
    """Decorator to write :file:`.current` file on function exit.

    See also:
        :doc:`/taskbars`

    Args:
        __fun: Function to wrap

    Returns:
        Wrapped function
    """

    @functools.wraps(__fun)
    def wrapper(*args, **kwargs):
        """Write value of ``task`` argument to ``.current`` on exit.

        Args:
            args: Positional arguments
            kwargs: Keyword arguments

        """
        globs = args[0]
        __fun(*args, **kwargs)
        with click.open_file(f'{globs.directory}/.current', 'w') as f:
            f.write(kwargs['task'])

    return wrapper


def remove_current(__fun: Callable) -> Callable:
    """Decorator to remove :file:`.current` file on function exit.

    See also:
        :doc:`/taskbars`

    Args:
        __fun: Function to wrap

    Returns:
        Wrapped function
    """

    @functools.wraps(__fun)
    def wrapper(*args, **kwargs):
        """Remove ``.current`` file on exit.

        Args:
            args: Positional arguments
            kwargs: Keyword arguments

        """
        globs = args[0]
        __fun(*args, **kwargs)
        if os.path.isfile(f'{globs.directory}/.current'):
            os.unlink(f'{globs.directory}/.current')

    return wrapper


def newer(__fname: str, __reference: str) -> bool:
    """Check whether given file is newer than reference file.

    Args:
        __fname: File to check
        __reference: file to test against

    Returns:
        ``True`` if ``__fname`` is newer than ``__reference``

    """
    return os.stat(__fname).st_mtime > os.stat(__reference).st_mtime


def term_link(__target: str, name: Optional[str] = None) -> str:
    """Generate a terminal hyperlink.

    See https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda.

    Args:
        __target: Hyperlink target
        name: Target name

    Returns:
        Formatted hyperlink for terminal output
    """
    if not name:
        name = os.path.basename(__target)
    return f'\033]8;;{__target}\007{name}\033]8;;\007'


def maybe_profile() -> ContextManager:  # pragma: no cover
    """Profile the wrapped code block.

    When :envvar:`RDIAL_PROFILE` is set execute the enclosed block under
    bprofile_.  The envvar’s value should be the name of the output file to
    generate.

    When :envvar:`RDIAL_PROFILE` is unset, this is just a no-op.

    .. _bprofile: https://pypi.org/project/bprofile/
    """
    profile = os.getenv('RDIAL_PROFILE')
    if profile:
        from bprofile import BProfile
        profiler = BProfile(profile)
    else:

        @contextmanager
        def noop():
            yield

        profiler = noop()
    return profiler
