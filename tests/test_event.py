#
#
"""test_event - Test database handling"""
# Copyright (C) 2011-2012  James Rowe <jnrowe@gmail.com>
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
from glob import glob

from expecter import expect
from nose2.tools import params

from rdial import (Events, isodate)


def test_read_datebase():
    expect(len(Events.read('tests/data/test'))) == 3


@params(
    (0, 'task', datetime(2011, 5, 4, 8, tzinfo=isodate.UTC),
     timedelta(hours=1)),
    (1, 'task2', datetime(2011, 5, 4, 9, 15, tzinfo=isodate.UTC),
     timedelta(minutes=15)),
    (2, 'task', datetime(2011, 5, 4, 9, 30, tzinfo=isodate.UTC), timedelta()),
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
    events._dirty = [e.task for e in events]
    try:
        events.write('tests/data/test_write')

        old_files = sorted(glob('tests/data/test/*.csv'))
        new_files = sorted(glob('tests/data/test_write/*.csv'))
        for old, new in zip(old_files, new_files):
            expect(open(old).read()) == open(new).read()
    finally:
        for i in os.listdir('tests/data/test_write'):
            os.unlink('tests/data/test_write/%s' % i)
        os.rmdir('tests/data/test_write')


def test_store_messages_with_events():
    events = Events.read('tests/data/test')
    expect(events.last().message) == 'finished'


def test_non_existing_database():
    expect(Events()) == Events.read("I_NEVER_EXIST")
