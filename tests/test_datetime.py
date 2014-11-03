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

from datetime import (datetime, timedelta)

from expecter import expect
from jnrbase.iso_8601 import utc
from nose2.tools import params

from rdial.utils import parse_datetime_user


@params(
    ('5 minutes ago', timedelta(minutes=5)),
    ('1 hour ago -5 minutes', timedelta(hours=1, minutes=5)),
)
def test_parse_datetime_via_date_command(string, delta):
    now = datetime.utcnow().replace(microsecond=0, tzinfo=utc)
    expect(parse_datetime_user(string)) == now - delta
