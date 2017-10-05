#
"""test_cmdline - Test command line functionality"""
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

from datetime import datetime

from click import BadParameter
from pytest import (mark, raises)

from rdial.cmdline import (StartTimeParamType, TaskNameParamType)


@mark.parametrize('string, expected', [
    ('valid_name', True),
    ('also-valid-name', True),
    ('.invalid_name', BadParameter),
    ('valid.name', True),
    ('invalid/name', BadParameter),
    ('', BadParameter),
    ('x' * 256, BadParameter),
    ('-bad-start', BadParameter),
])
def test_task_name_validity(string, expected):
    p = TaskNameParamType()
    if expected is True:
        assert p.convert(string, None, None) == string
    else:
        with raises(expected):
            p.convert(string, None, None)


@mark.parametrize('string, expected', [
    ('yesterday', True),
    ('', True),
    ('2011-05-04T09:15:00Z', True),
    ('AB1 time', BadParameter),
])
def test_start_time_validity(string, expected):
    p = StartTimeParamType()
    if expected is True:
        assert isinstance(p.convert(string, None, None), datetime)
    else:
        with raises(expected):
            p.convert(string, None, None)
