#
#
"""xdg_basedir_tests - Test XDG base directory support"""
# Copyright (C) 2011-2012  James Rowe <jnrowe@gmail.com>
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
from nose.tools import assert_equal

import rdial


@patch('rdial.os.getenv')
def test_no_args(getenv):
    getenv.return_value = '~/.local/share'
    assert_equal(rdial.xdg_data_location(), '~/.local/share/rdial')


@patch('rdial.os.getenv')
def test_no_home(getenv):
    getenv.side_effect = lambda k, v: v
    assert_equal(rdial.xdg_data_location(), '/.local/share/rdial')
