#
# coding=utf-8
"""switch - CLI ``switch`` command for rdial"""
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

from .base import (Command, task_parser)


class Switch(Command):
    """Complete last task and start new one."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
            parents=[task_parser, ],
            add_help=False,
        )

        parser.add_argument('-n', '--new', action='store_true',
                            help=_('start a new task'))
        parser.add_argument('-m', '--message',
                            help=_('closing message for current task'))
        parser.add_argument('-F', '--file', type=argparse.FileType(),
                            help=_('read closing message for current task from file'))
        return parser

    def take_action(self, parsed_args):
        self.log.debug('entering %r' % __name__)

        if parsed_args.file:
            parsed_args.message = file.read()
        if parsed_args.new or parsed_args.task in self.app.events.tasks():
            # This is dirty, but we kick on to Events.start() to save
            # duplication of error handling for task names
            self.app.events.stop(parsed_args.message)
        self.app.events.start(parsed_args.task, parsed_args.new)
        open('%s/.current' % self.app.options.directory, 'w').write(parsed_args.task)
