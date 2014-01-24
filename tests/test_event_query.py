#
# coding=utf-8
"""test_event_query - Test event query handling"""
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

from datetime import timedelta

from expecter import expect

from rdial.events import Events


def test_list_tasks():
    events = Events.read('tests/data/test')
    expect(events.tasks()) == ['task', 'task2']


def test_current_running_event():
    events = Events.read('tests/data/test')
    expect(events.running()) == 'task'


def test_no_currently_running_event():
    events = Events.read('tests/data/test_not_running')
    expect(events.running()) is False


def test_sum_durations_in_database():
    events = Events.read('tests/data/test_not_running')
    expect(events.sum()) == timedelta(hours=2, minutes=15)
