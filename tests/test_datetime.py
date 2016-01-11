#
# coding=utf-8
"""test_datetime - Test ISO-8601 handling"""
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

from datetime import (datetime, timedelta)

from expecter import expect
from nose2.tools import params

from rdial.utils import (format_datetime, parse_datetime, parse_datetime_user,
                         UTC)


@params(
    ('2011-05-04T08:00:00Z', datetime(2011, 5, 4, 8, 0, tzinfo=UTC())),
    ('2011-05-04T09:15:00Z', datetime(2011, 5, 4, 9, 15, tzinfo=UTC())),
    ('2011-05-04T10:15:00+0100', datetime(2011, 5, 4, 9, 15, tzinfo=UTC())),
)
def test_parse_datetime(string, expected):
    expect(parse_datetime(string)) == expected


@params(
    ('5 minutes ago', timedelta(minutes=5)),
    ('1 hour ago -5 minutes', timedelta(hours=1, minutes=5)),
)
def test_parse_datetime_via_date_command(string, delta):
    now = datetime.utcnow().replace(microsecond=0, tzinfo=UTC())
    # Accept a 2.5 second smudge window
    expect(parse_datetime_user(string)) >= now - delta
    expect(parse_datetime_user(string)) < now - delta + timedelta(seconds=2.5)


@params(
    (datetime(2011, 5, 4, 8, 0, tzinfo=UTC()), '2011-05-04T08:00:00Z'),
    (datetime(2011, 5, 4, 9, 15, tzinfo=UTC()), '2011-05-04T09:15:00Z'),
)
def test_format_datetime(dt, expected):
    expect(format_datetime(dt)) == expected
