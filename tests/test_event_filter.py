#
"""test_event_filter - Test event filter handling"""
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
#
# SPDX-License-Identifier: GPL-3.0+

from typing import Dict, List, Optional

from jnrbase.attrdict import AttrDict
from pytest import mark

from rdial.cmdline import filter_events
from rdial.events import Events


def test_fetch_events_for_task():
    events = Events.read('tests/data/test', write_cache=False)
    assert len(events.for_task(task='task2')) == 1


@mark.parametrize('date, expected', [
    ({'year': 2011, }, 2),
    ({'year': 2011, 'month': 1}, 1),
    ({'year': 2011, 'month': 3, 'day': 1}, 1),
    ({'year': 2011, 'month': 3, 'day': 31}, 0),
])
def test_fetch_events_for_date(date: Dict[str, int], expected: int):
    events = Events.read('tests/data/date_filtering', write_cache=False)
    assert len(events.for_date(**date)) == expected


def test_fetch_events_for_week():
    events = Events.read('tests/data/date_filtering', write_cache=False)
    assert len(events.for_week(year=2011, week=9)) == 1


@mark.parametrize('task, result', [
    (None, ['task', 'task2']),
    ('task', ['task', ]),
])
def test_filter_events_by_task(task: Optional[str], result: List[str]):
    globs = AttrDict(directory='tests/data/test', cache=False)
    evs = filter_events(globs, task)
    assert evs.tasks() == result
