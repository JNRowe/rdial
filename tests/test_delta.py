#
# coding=utf-8
"""test_delta - Test ISO-8601 delta handling"""
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

from datetime import timedelta

from nose2.tools import params

from rdial.utils import (format_delta, parse_delta)


@params(
    ('PT04H30M21S', timedelta(hours=4, minutes=30, seconds=21)),
    ('PT00H12M01S', timedelta(minutes=12, seconds=1)),
)
def test_parse_duration(string, expected):
    parse_delta(string).must.equal(expected)


@params(
    (timedelta(hours=4, minutes=30, seconds=21), 'PT04H30M21S'),
    (timedelta(minutes=12, seconds=1), 'PT12M01S'),
)
def test_format_duration(delta, expected):
    format_delta(delta).must.equal(expected)


def test_parse_null_duration():
    parse_delta('').must.equal(timedelta())


def test_format_zero_duration():
    format_delta(timedelta()).must.equal('')


@params(
    ('PT04H', timedelta(hours=4)),
    ('PT04H30M', timedelta(hours=4, minutes=30)),
    ('PT30M', timedelta(minutes=30)),
    ('PT04H21S', timedelta(hours=4, seconds=21)),
    ('PT4H', timedelta(hours=4)),
)
def test_parse_partially_defined_durations(string, expected):
    parse_delta(string).must.equal(expected)


@params(
    ('P3DT04H', timedelta(days=3, hours=4)),
    ('P3D', timedelta(days=3)),
)
def test_parse_durations_with_days(string, expected):
    parse_delta(string).must.equal(expected)


@params(
    (timedelta(days=3, hours=4), 'P3DT04H'),
    (timedelta(days=3), 'P3D'),
    (timedelta(days=2, hours=22), 'P2DT22H'),
)
def test_format_durations_with_days(delta, expected):
    format_delta(delta).must.equal(expected)


@params(
    (timedelta(hours=4), 'PT04H'),
    (timedelta(hours=4, minutes=30), 'PT04H30M'),
    (timedelta(minutes=30), 'PT30M'),
    (timedelta(hours=4, seconds=21), 'PT04H21S'),
)
def test_format_partially_defined_durations(delta, expected):
    format_delta(delta).must.equal(expected)
