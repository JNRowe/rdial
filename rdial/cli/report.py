#
# coding=utf-8
"""report - CLI ``report`` command for rdial"""
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

import isodate
import prettytable

from rdial.i18n import (N_, _)

from .base import (Command, duration_parser, filter_events, task_parser)


class Report(Command):
    """Report time tracking data."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
            parents=[duration_parser, task_parser],
            add_help=False,
        )

        output_group = parser.add_mutually_exclusive_group()
        output_group.add_argument('--html', action='store_true',
                                  help=_('produce HTML output'))
        output_group.add_argument('--human', action='store_true',
                                  help=_('produce human-readable output'))

        parser.add_argument('-s', '--sort', default='task',
                            choices=['task', 'time'],
                            help=_('field to sort by'))
        parser.add_argument('-r', '--reverse', action='store_true',
                            help=_('reverse sort order'))
        return parser

    def take_action(self, parsed_args):
        self.log.debug('entering %r' % __name__)

        if parsed_args.task == 'default':
            # Lazy way to remove duplicate argument definitions
            parsed_args.task = None
        events = filter_events(self.app.events, parsed_args.task,
                               parsed_args.duration)
        if parsed_args.human:
            print(N_('%d event in query', '%d events in query', len(events))
                  % len(events))
            print(_('Duration of events %s') % events.sum())
            print(_('First entry started at %s') % events[0].start)
            print(_('Last entry started at %s') % events[-1].start)
            dates = set(e.start.date() for e in events)
            print(_('Events exist on %d dates') % len(dates))
        else:
            table = prettytable.PrettyTable(['task', 'time'])
            formatter = table.get_html_string if parsed_args.html else table.get_string
            try:
                table.align['task'] = 'l'
            except AttributeError:  # prettytable 0.5 compatibility
                table.set_field_align('task', 'l')
            for task in events.tasks():
                table.add_row([task, events.for_task(task).sum()])

            print(formatter(sortby=parsed_args.sort,
                            reversesort=parsed_args.reverse))
        if events.running() and not parsed_args.html:
            current = events.last()
            print(_("Running `%s' since %s")
                  % (current.task, isodate.datetime_isoformat(current.start)))
