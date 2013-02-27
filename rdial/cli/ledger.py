#
# coding=utf-8
"""ledger - CLI ``ledger`` command for rdial"""
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

from cliff.command import Command

from rdial.i18n import _

from .base import (duration_parser, filter_events, task_parser)


class Ledger(Command):
    """Generate ledger compatible data file."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
            parents=[duration_parser, task_parser, ],
            add_help=False,
        )

        parser.add_argument('-r', '--rate', metavar='rate',
                            help=_('hourly rate for task output'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug('entering %r' % __name__)

        if parsed_args.task == 'default':
            # Lazy way to remove duplicate argument definitions
            parsed_args.task = None
        events = filter_events(self.app.events, parsed_args.task,
                               parsed_args.duration)
        if events.running():
            print(_(';; Running event not included in output!'))
        for event in events:
            if not event.delta:
                break
            end = event.start + event.delta
            # Can't use timedelta.total_seconds() as it was only added in 2.7
            seconds = event.delta.days * 86400 + event.delta.seconds
            hours = seconds / 3600.0
            print('%s-%s' % (event.start.strftime('%Y-%m-%d * %H:%M'),
                             end.strftime('%H:%M')))
            print('    (task:%s)  %.2fh%s'
                  % (event.task, hours,
                     ' @ %s' % parsed_args.rate if parsed_args.rate else ''))
        if events.running():
            print(_(';; Running event not included in output!'))
