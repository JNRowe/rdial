#
# coding=utf-8
"""last - CLI ``last`` command for rdial"""
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


class Last(Command):
    """Display last event, if any."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug('entering %r' % __name__)

        event = self.app.events.last()
        if event.delta:
            print(_('Last task %s, ran for %s') % (event.task, event.delta))
        else:
            print(utils.warn(_('Task %s is still running') % event.task))
