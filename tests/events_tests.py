#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""event_tests - Test Events methods"""
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

import unittest

from nose.tools import assert_equal

from rdial import Events


class NoFileTest(unittest.TestCase):
    """Should return empty Events with non-existent file"""

    def test_no_file(self):
        assert_equal(Events(), Events.read("I_NEVER_EXIST"))
