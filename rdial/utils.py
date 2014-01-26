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

try:  # For Python 3
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser  # NOQA

import arrow
import blessings

from . import compat
from .i18n import _


T = blessings.Terminal()


# Set up informational message functions
def _colourise(text, colour):
    """Colour text, if possible.

    :param str text: Text to colourise
    :param str colour: Colour to display text in
    :rtype: :obj:`str`
    :return str: Colourised text, if possible

    """
    return getattr(T, colour.replace(' ', '_'))(text)


def success(text):
    """Pretty print a success message.

    :param str text: Text to format
    :rtype: :obj:`str`
    :return: Bright green text, if possible

    """
    return _colourise(text, 'bright green')


def fail(text):
    """Pretty print a failure message.

    :param str text: Text to format
    :rtype: :obj:`str`
    :return: Bright red text, if possible

    """
    return _colourise(text, 'bright red')


def warn(text):
    """Pretty print a warning message.

    :param str text: Text to format
    :rtype: ``str``
    :return: Bright yellow text, if possible

    """
    return _colourise(text, 'bright yellow')


class RdialError(ValueError):

    """Generic exception for rdial."""

    if not compat.PY2:
        @property
        def message(self):
            """Compatibility hack for Python 3."""
            return self.args[0]


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
    """Parse ISO-8601 datetime string.

    :param str string: Datetime string to parse
    :rtype: :obj:`arrow.Arrow`
    :return: Parsed datetime object

    """
    if not string:
        datetime_ = arrow.now()
    else:
        datetime_ = arrow.get(string)
    return datetime_


def format_datetime(datetime_):
    """Format ISO-8601 datetime string.

    :param arrow.Arrow datetime_: Datetime to process
    :rtype: str
    :return: ISO-8601 compatible string

    """
    # Can't call str method as it uses the verbose microsecond form, and
    # doesn't collapse UTC timezone in the manner I like
    return datetime_.to('utc').format('YYYY-MM-DDTHH:mm:ss') + 'Z'


def iso_week_to_date(year, week):
    """Generate date range for a given ISO-8601 week.

    ISO-8601 defines a week as Monday to Sunday, with the first week of a year
    being the first week containing a Thursday.

    :param int year: Year to process
    :param int week: Week number to process
    :rtype: :obj:`tuple` of :obj:`arrow.Arrow`
    :return: Date range objects for given week

    """
    iso_start = arrow.get(year, 1, 4).floor('week')
    start = iso_start.replace(weeks=week - 1)
    end = start.replace(weeks=1)
    return start, end


def read_config(parser, user_config=None):
    """Read configuration data.

    :type argparse.ArgumentParser parser: Command line parser
    :type str user_config: User defined config file
    :rtype: ConfigParser
    :return: Parsed configuration data

    """
    if user_config and not os.path.exists(user_config):
        raise parser.error(_("Config file %r doesn't exist!" % user_config))

    configs = [os.path.dirname(__file__) + '/config', ]
    for s in os.getenv('XDG_CONFIG_DIRS', '/etc/xdg').split(':'):
        p = s + '/rdial/config'
        if os.path.isfile(p):
            configs.append(p)
    configs.append(xdg_config_location() + '/config')
    configs.append(os.path.abspath('.rdialrc'))
    if user_config:
        configs.append(user_config)
    cfg = ConfigParser()
    for file in configs:
        if os.path.isfile(file):
            cfg.readfp(compat.open(file, encoding='utf-8'))

    return cfg


def write_current(f):
    """Decorator to write ``current`` file on function exit.

    :seealso: :doc:`/taskbars`

    :rtype: obj:`function`

    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        open('%s/.current' % kwargs['directory'], 'w').write(kwargs['task'])
    return wrapper


def remove_current(f):
    """Decorator to remove ``current`` file on function exit.

    :seealso: :doc:`/taskbars`

    :rtype: obj:`function`

    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        if os.path.isfile('%s/.current' % kwargs['directory']):
            os.unlink('%s/.current' % kwargs['directory'])
    return wrapper


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
