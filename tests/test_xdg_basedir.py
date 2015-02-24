#
# coding=utf-8
"""test_xdg_basedir - Test XDG base directory support"""
# Copyright © 2011-2015  James Rowe <jnrowe@gmail.com>
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

from mock import patch

from rdial.utils import (xdg_config_location, xdg_data_location)


def test_config_no_args():
    with patch.dict('os.environ', {'XDG_CONFIG_HOME': '~/.xdg/config'}):
        xdg_config_location().must.equal('~/.xdg/config/rdial')


def test_config_no_home():
    with patch.dict('os.environ', clear=True):
        xdg_config_location().must.equal('/.config/rdial')


def test_data_no_args():
    with patch.dict('os.environ', {'XDG_DATA_HOME': '~/.xdg/local'}):
        xdg_data_location().must.equal('~/.xdg/local/rdial')


def test_data_no_home():
    with patch.dict('os.environ', clear=True):
        xdg_data_location().must.equal('/.local/share/rdial')
