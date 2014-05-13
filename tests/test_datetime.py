#
# coding=utf-8
"""test_datetime - Test ISO-8601 handling"""
# Copyright © 2011-2014  James Rowe <jnrowe@gmail.com>
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

from datetime import datetime

from expecter import expect
from nose2.tools import params

from rdial.utils import (format_datetime, parse_datetime, utc)


@params(
    ('2011-05-04T08:00:00Z', datetime(2011, 5, 4, 8, 0, tzinfo=utc)),
    ('2011-05-04T09:15:00Z', datetime(2011, 5, 4, 9, 15, tzinfo=utc)),
)
def test_parse_datetime(string, expected):
    expect(parse_datetime(string)) == expected


@params(
    (datetime(2011, 5, 4, 8, 0, tzinfo=utc), '2011-05-04T08:00:00Z'),
    (datetime(2011, 5, 4, 9, 15, tzinfo=utc), '2011-05-04T09:15:00Z'),
)
def test_format_datetime(dt, expected):
    expect(format_datetime(dt)) == expected
