#
"""test_setup_py - Test setup.py functionality"""
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

from pytest import mark

import setup


@mark.parametrize('input, expected', [
    ('plain', ['tabulate', ]),
    ('recurse', ['click', 'tabulate', ]),
])
def test_parse_requires(input, expected):
    requires = setup.parse_requires(
        '../tests/data/requires/{}.txt'.format(input))
    assert requires == expected
