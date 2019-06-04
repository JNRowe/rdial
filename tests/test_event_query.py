#
"""test_event_query - Test event query handling."""
# Copyright © 2011-2019  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0+
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

from datetime import timedelta

from rdial.events import Events


def test_list_tasks():
    events = Events.read('tests/data/test', write_cache=False)
    assert events.tasks() == ['task', 'task2']


def test_current_running_event():
    events = Events.read('tests/data/test', write_cache=False)
    assert events.running() == 'task'


def test_no_currently_running_event():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    assert not events.running()


def test_sum_durations_in_database():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    assert events.sum() == timedelta(hours=2, minutes=15)
