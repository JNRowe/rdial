#
"""test_event - Test database handling"""
# Copyright © 2012-2017  James Rowe <jnrowe@gmail.com>
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
from filecmp import dircmp
from os.path import abspath
from warnings import (catch_warnings, simplefilter)

from click.testing import CliRunner
from expecter import expect
from nose2.tools import params
from jnrbase.iso_8601 import (parse_datetime, parse_delta)

from rdial.events import (Event, Events)


@params(
    ('test', None, None, None),
    ('test', '2013-02-26T19:45:14', None, None),
    ('test', datetime(2013, 2, 26, 19, 45, 14), None,
     None),
    ('test', '2013-02-26T19:45:14', 'PT8M19S', None),
    ('test', '2013-02-26T19:45:14', timedelta(minutes=8, seconds=19.770869),
     None),
    ('test', '2013-02-26T19:45:14', 'PT8M19S', 'stopped'),
)
def test_event_creation(task, start, delta, message):
    e = Event(task, start, delta, message)
    expect(e.task) == task
    if isinstance(start, datetime):
        expect(e.start) == start
    elif start:
        expect(e.start) == parse_datetime(start, naive=True)
    else:
        # Special case to ignore comparison against utcnow()
        pass
    if isinstance(delta, timedelta):
        expect(e.delta) == delta
    else:
        expect(e.delta) == parse_delta(delta)
    expect(e.message) == message


@params(
    ('test', 3),
    ('date_filtering', 3),
    ('test_not_running', 3),
)
def test_read_datebase(database, events):
    evs = Events.read('tests/data/' + database, write_cache=False)
    expect(len(evs)) == events


@params(
    ('test', 3),
    ('date_filtering', 3),
    ('test_not_running', 3),
)
def test_read_datebase_wrapper(database, events):
    with Events.wrapping('tests/data/' + database, write_cache=False) as evs:
        expect(len(evs)) == events


def test_read_datebase_context(database, events):
    with catch_warnings(record=True) as warns:
        simplefilter("always")
        with Events.context('tests/data/test', write_cache=False):
            pass
        expect(warns[0].category) == DeprecationWarning
        expect(str(warns[0])).contains('to wrapping')


@params(
    (0, 'task', datetime(2011, 5, 4, 8),
     timedelta(hours=1)),
    (1, 'task2', datetime(2011, 5, 4, 9, 15),
     timedelta(minutes=15)),
    (2, 'task', datetime(2011, 5, 4, 9, 30), timedelta()),
)
def test_check_events(n, task, start, delta):
    # FIXME: Clean-ish way to perform check, with the caveat that it parses the
    # database on each entry.  Need a better solution.
    events = Events.read('tests/data/test', write_cache=False)
    expect(events[n].task) == task
    expect(events[n].start) == start
    expect(events[n].delta) == delta


def test_write_database():
    runner = CliRunner()
    in_dir = abspath('tests/data/test')
    events = Events.read(in_dir, write_cache=False)
    events._dirty = events.tasks()
    with runner.isolated_filesystem() as tempdir:
        events.write(tempdir)
        comp = dircmp(in_dir, tempdir)
        expect(comp.diff_files) == []
        expect(comp.left_only) == []
        expect(comp.right_only) == []
        expect(comp.funny_files) == []


def test_store_messages_with_events():
    events = Events.read('tests/data/test', write_cache=False)
    expect(events.last().message) == 'finished'


def test_non_existing_database():
    expect(Events()) == Events.read('I_NEVER_EXIST', write_cache=False)
