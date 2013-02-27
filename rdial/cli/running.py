#
# coding=utf-8
"""running - CLI ``running`` command for rdial"""
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

import logging

from cliff.command import Command

from rdial import utils
from rdial.i18n import _


class Running(Command):
    """Display running task, if any.

    :param str directory: Directory to read events from
    :param bool backup: Whether to create backup files

    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug('entering %r' % __name__)

        if self.app.events.running():
            current = self.app.events.last()
            print(_('Task %s has been running for %s')
                  % (current.task,
                     str(utils.utcnow() - current.start).split('.')[0]))
        else:
            print(utils.warn(_('No task is running!')))
