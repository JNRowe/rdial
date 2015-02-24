#
# coding=utf-8
"""test_event - Test database handling"""
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


from datetime import (datetime, timedelta)
from filecmp import dircmp
from os.path import abspath

from click.testing import CliRunner
from nose2.tools import params

from rdial.events import (Event, Events)
from rdial.utils import (parse_datetime, parse_delta, UTC)


@params(
    ('test', None, None, None),
    ('test', '2013-02-26T19:45:14Z', None, None),
    ('test', datetime(2013, 2, 26, 19, 45, 14, tzinfo=UTC()), None,
     None),
    ('test', '2013-02-26T19:45:14Z', 'PT8M19.770869S', None),
    ('test', '2013-02-26T19:45:14Z', timedelta(minutes=8, seconds=19.770869),
     None),
    ('test', '2013-02-26T19:45:14Z', 'PT8M19.770869S', 'stopped'),
)
def test_event_creation(task, start, delta, message):
    e = Event(task, start, delta, message)
    e.task.must.equal(task)
    if isinstance(start, datetime):
        e.start.must.equal(start)
    elif start:
        e.start.must.equal(parse_datetime(start))
    else:
        # Special case to ignore comparison against utcnow()
        pass
    if isinstance(delta, timedelta):
        e.delta.must.equal(delta)
    else:
        e.delta.must.equal(parse_delta(delta))
    e.message.must.equal(message)


@params(
    ('test', 3),
    ('date_filtering', 3),
    ('test_not_running', 3),
)
def test_read_datebase(database, events):
    evs = Events.read('tests/data/' + database, write_cache=False)
    evs.must.have.length_of(events)


@params(
    (0, 'task', datetime(2011, 5, 4, 8, tzinfo=UTC()),
     timedelta(hours=1)),
    (1, 'task2', datetime(2011, 5, 4, 9, 15, tzinfo=UTC()),
     timedelta(minutes=15)),
    (2, 'task', datetime(2011, 5, 4, 9, 30, tzinfo=UTC()), timedelta()),
)
def test_check_events(n, task, start, delta):
    # FIXME: Clean-ish way to perform check, with the caveat that it parses the
    # database on each entry.  Need a better solution.
    events = Events.read('tests/data/test', write_cache=False)
    events[n].task.must.equal(task)
    events[n].start.must.equal(start)
    events[n].delta.must.equal(delta)


def test_write_database():
    runner = CliRunner()
    in_dir = abspath('tests/data/test')
    events = Events.read(in_dir, write_cache=False)
    events._dirty = events.tasks()
    with runner.isolated_filesystem() as tempdir:
        events.write(tempdir)
        comp = dircmp(in_dir, tempdir)
        comp.diff_files.must.be.empty
        comp.left_only.must.be.empty
        comp.right_only.must.be.empty
        comp.funny_files.must.be.empty


def test_store_messages_with_events():
    events = Events.read('tests/data/test', write_cache=False)
    events.last().message.must.equal('finished')


def test_non_existing_database():
    Events().must.equal(Events.read('I_NEVER_EXIST', write_cache=False))
