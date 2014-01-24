#
# coding=utf-8
"""test_event - Test database handling"""
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

import os

from datetime import (datetime, timedelta)
from filecmp import dircmp

from expecter import expect
from nose2.tools import params

from rdial.events import (Event, Events)
from rdial.utils import (parse_datetime, parse_delta, utc)


@params(
    ('test', None, None, None),
    ('test', '2013-02-26T19:45:14Z', None, None),
    ('test', datetime(2013, 2, 26, 19, 45, 14, tzinfo=utc), None,
     None),
    ('test', '2013-02-26T19:45:14Z', 'PT8M19.770869S', None),
    ('test', '2013-02-26T19:45:14Z', timedelta(minutes=8, seconds=19.770869),
     None),
    ('test', '2013-02-26T19:45:14Z', 'PT8M19.770869S', 'stopped'),
)
def test_event_creation(task, start, delta, message):
    e = Event(task, start, delta, message)
    expect(e.task) == task
    if isinstance(start, datetime):
        expect(e.start) == start
    elif start:
        expect(e.start) == parse_datetime(start)
    else:
        # Special case to ignore comparison against utcnow()
        pass
    if isinstance(delta, timedelta):
        expect(e.delta) == delta
    else:
        expect(e.delta) == parse_delta(delta)
    expect(e.message) == message


def test_read_datebase():
    expect(len(Events.read('tests/data/test'))) == 3


@params(
    (0, 'task', datetime(2011, 5, 4, 8, tzinfo=utc),
     timedelta(hours=1)),
    (1, 'task2', datetime(2011, 5, 4, 9, 15, tzinfo=utc),
     timedelta(minutes=15)),
    (2, 'task', datetime(2011, 5, 4, 9, 30, tzinfo=utc), timedelta()),
)
def test_check_events(n, task, start, delta):
    # FIXME: Clean-ish way to perform check, with the caveat that it parses the
    # database on each entry.  Need a better solution.
    events = Events.read('tests/data/test')
    expect(events[n].task) == task
    expect(events[n].start) == start
    expect(events[n].delta) == delta


def test_write_database():
    events = Events.read('tests/data/test')
    events._dirty = events.tasks()
    try:
        events.write('tests/data/test_write')

        comp = dircmp('tests/data/test', 'tests/data/test_write')
        expect(comp.diff_files) == []
        expect(comp.left_only) == []
        expect(comp.right_only) == []
        expect(comp.funny_files) == []
    finally:
        for i in os.listdir('tests/data/test_write'):
            os.unlink('tests/data/test_write/%s' % i)
        os.rmdir('tests/data/test_write')


def test_store_messages_with_events():
    events = Events.read('tests/data/test')
    expect(events.last().message) == 'finished'


def test_non_existing_database():
    expect(Events()) == Events.read('I_NEVER_EXIST')
