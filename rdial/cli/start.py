#
# coding=utf-8
"""start - CLI ``start`` command for rdial"""
# Copyright © 2012, 2013  James Rowe <jnrowe@gmail.com>
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

import argparse
import logging

from rdial.i18n import _
from rdial.utils import parse_datetime

from .base import (Command, task_parser)


def start_time_typecheck(string):
    """Check given start time is valid.

    :param str string: Timestamps to check
    :rtype: :obj:`str`
    :returns: Timestamp, if valid
    :raises argparse.ArgparseTypeError: If timestamp is invalid

    """
    try:
        parse_datetime(string)
    except ValueError:
        raise argparse.ArgumentTypeError(_('%r is not a valid ISO-8601 time '
                                           'string') % string)
    return string


class Start(Command):
    """Start task."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
            parents=[task_parser],
            add_help=False,
        )

        parser.add_argument('-n', '--new', action='store_true',
                            help=_('start a new task'))
        parser.add_argument('-t', '--time', metavar='time', default='',
                            help=_('set start time'),
                            type=start_time_typecheck)

        return parser

    def take_action(self, parsed_args):
        self.log.debug('entering %r' % __name__)

        self.app.events.start(parsed_args.task, parsed_args.new,
                              parsed_args.time)
        open('%s/.current' % self.app.options.directory, 'w').write(parsed_args.task)
