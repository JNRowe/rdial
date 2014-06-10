#
# coding=utf-8
"""test_week - Test ISO-8601 week handling"""
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

from datetime import date

from expecter import expect
from nose2.tools import params

from rdial.utils import iso_week_to_date


@params(
    (2007, 1, (date(2007, 1, 1), date(2007, 1, 8))),  # Year starts same day
    (2009, 53, (date(2009, 12, 28), date(2010, 1, 4))),  # ISO year spans 2010
    (2013, 52, (date(2013, 12, 23), date(2013, 12, 30))),
)
def test_iso_week_to_date(year, week, expected):
    expect(iso_week_to_date(year, week)) == expected
