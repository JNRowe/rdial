#
# coding=utf-8
"""test_xdg_basedir - Test XDG base directory support"""
# Copyright © 2011-2016  James Rowe <jnrowe@gmail.com>
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

from expecter import expect
from mock import patch

from rdial.utils import (xdg_config_location, xdg_data_location)


def test_config_no_args():
    with patch.dict('os.environ', {'XDG_CONFIG_HOME': '~/.xdg/config'}):
        expect(xdg_config_location()) == '~/.xdg/config/rdial'


def test_config_no_home():
    with patch.dict('os.environ', clear=True):
        expect(xdg_config_location()) == '/.config/rdial'


def test_data_no_args():
    with patch.dict('os.environ', {'XDG_DATA_HOME': '~/.xdg/local'}):
        expect(xdg_data_location()) == '~/.xdg/local/rdial'


def test_data_no_home():
    with patch.dict('os.environ', clear=True):
        expect(xdg_data_location()) == '/.local/share/rdial'
