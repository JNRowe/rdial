#
# coding=utf-8
"""cmdline - Command line functionality for rdial"""
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
import os
import sys

try:
    import configparser
except ImportError:  # Python 3
    import ConfigParser as configparser  # NOQA

from cliff.app import App
from cliff.commandmanager import CommandManager

from . import _version
from .events import Events
from .i18n import _
from .utils import (xdg_config_location, xdg_data_location)


class RdialApp(App):
    log = logging.getLogger(__name__)

    def __init__(self):
        super(RdialApp, self).__init__(
            description=__doc__.splitlines()[0].split("-", 1)[1],
            version=_version.dotted,
            command_manager=CommandManager('rdial.cli')
        )

    def build_option_parser(self, *args, **kwargs):
        configs = [os.path.dirname(__file__) + '/config', ]
        for s in os.getenv('XDG_CONFIG_DIRS', '/etc/xdg').split(':'):
            p = s + '/rdial/config'
            if os.path.isfile(p):
                configs.append(p)
        configs.append(xdg_config_location() + '/config')
        configs.append(os.path.abspath('.rdialrc'))
        cfg = configparser.SafeConfigParser()
        cfg.read(configs)

        parser = super(RdialApp, self).build_option_parser(
            *args,
            argparse_kwargs={
                'epilog': _("Please report bugs to jnrowe@gmail.com")
            },
            **kwargs
        )
        parser.add_argument('-d', '--directory', metavar='dir',
                            help=_('directory to read/write to'))
        parser.add_argument('--no-backup', dest='backup', action='store_true',
                            help=_('do not write data file backups'))
        parser.set_defaults(backup=not cfg.getboolean('rdial', 'backup'),
                            directory=cfg.get('rdial', 'directory',
                                              vars={'xdg_data_location':
                                                    xdg_data_location()}))
        return parser

    def initialize_app(self, argv):
        self.log.debug('Reading events from database')
        self.events = Events.read(self.options.directory)

    def clean_up(self, cmd, result, err):
        if err:
            self.log.debug('got an error: %s', err)
        if self.events.dirty:
            self.log.debug('Writing events to database')
            self.events.write(self.options.directory)


def main(argv=sys.argv[1:]):
    rdial_app = RdialApp()
    return rdial_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
