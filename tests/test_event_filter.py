#
# coding=utf-8
"""test_event_filter - Test event filter handling"""
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

from nose2.tools import params

from rdial.events import Events


def test_fetch_events_for_task():
    events = Events.read('tests/data/test', write_cache=False)
    events.for_task(task='task2').must.have.length_of(1)


@params(
    ({'year': 2011, }, 2),
    ({'year': 2011, 'month': 1}, 1),
    ({'year': 2011, 'month': 3, 'day': 1}, 1),
    ({'year': 2011, 'month': 3, 'day': 31}, 0),
)
def test_fetch_events_for_date(date, expected):
    events = Events.read('tests/data/date_filtering', write_cache=False)
    events.for_date(**date).must.have.length_of(expected)


def test_fetch_events_for_week():
    events = Events.read('tests/data/date_filtering', write_cache=False)
    events.for_week(year=2011, week=9).must.have.length_of(1)
