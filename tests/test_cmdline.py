#
# coding=utf-8
"""test_cmdline - Test command line functionality"""
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

from click import BadParameter
from expecter import expect
from nose2.tools import params

from rdial.cmdline import (StartTimeParamType, TaskNameParamType)


@params(
    ('valid_name', True),
    ('also-valid-name', True),
    ('.invalid_name', BadParameter),
    ('valid.name', True),
    ('invalid/name', BadParameter),
    ('', BadParameter),
    ('x' * 256, BadParameter),
)
def test_task_name_validity(string, expected):
    p = TaskNameParamType()
    if expected is True:
        expect(p.convert(string, None, None) == string)
    else:
        with expect.raises(expected):
            p.convert(string, None, None)


@params(
    ('yesterday', True),
    ('', True),
    ('2011-05-04T09:15:00Z', True),
    ('AB1 time', BadParameter),
)
def test_start_time_validity(string, expected):
    p = StartTimeParamType()
    if expected is True:
        expect(p.convert(string, None, None) == string)
    else:
        with expect.raises(expected):
            p.convert(string, None, None)
