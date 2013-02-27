#
# coding=utf-8
"""stop - CLI ``stop`` command for rdial"""
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
import os

from cliff.command import Command

from rdial.i18n import _


class Stop(Command):
    """Stop task."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
            add_help=False,
        )

        parser.add_argument('-m', '--message', metavar='message',
                            help=_('closing message'))
        parser.add_argument('-F', '--file', metavar='file',
                            type=argparse.FileType(),
                            help=_('read closing message from file'))
        parser.add_argument('--amend', action='store_true',
                            help=_('amend previous stop entry'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug('entering %r' % __name__)

        if parsed_args.file:
            parsed_args.message = file.read()
        if parsed_args.amend and not parsed_args.message:
            event = self.app.events.last()
            parsed_args.message = event.message
        self.app.events.stop(parsed_args.message, force=parsed_args.amend)
        event = self.app.events.last()
        print(_('Task %s running for %s') % (event.task,
                                             str(event.delta).split('.')[0]))
        if os.path.isfile('%s/.current' % self.app.options.directory):
            os.unlink('%s/.current' % self.app.options.directory)
