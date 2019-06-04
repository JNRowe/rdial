#
"""test_event - Test database handling."""
# Copyright © 2012-2019  James Rowe <jnrowe@gmail.com>
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

from datetime import datetime, timedelta, timezone
from filecmp import dircmp
from glob import glob
from shutil import copytree
from typing import Optional, Union

from jnrbase.iso_8601 import parse_datetime, parse_delta
from pytest import fixture, mark, raises

from rdial import events as events_mod
from rdial.events import Event, Events, TaskRunningError


@fixture
def temp_user_cache(monkeypatch, tmpdir):
    cache_dir = tmpdir.join('cache')
    cache_dir.mkdir()
    monkeypatch.setattr(events_mod.xdg_basedir, 'user_cache',
                        lambda s: cache_dir.strpath)


@mark.parametrize('task, start, delta, message', [
    ('test', None, None, None),
    ('test', '2013-02-26T19:45:14', None, None),
    ('test', datetime(2013, 2, 26, 19, 45, 14), None, None),
    ('test', '2013-02-26T19:45:14', 'PT8M19S', None),
    ('test', '2013-02-26T19:45:14', timedelta(minutes=8, seconds=19.770869),
     None),
    ('test', '2013-02-26T19:45:14', 'PT8M19S', 'stopped'),
])
def test_event_creation(task: str, start: Optional[Union[str, datetime]],
                        delta: Optional[Union[str, timedelta]], message: str):
    e = Event(task, start, delta, message)
    assert e.task == task
    if isinstance(start, datetime):
        assert e.start == start
    elif start:
        assert e.start == parse_datetime(start).replace(tzinfo=None)
    else:
        # Special case to ignore comparison against utcnow()
        pass
    if isinstance(delta, timedelta):
        assert e.delta == delta
    else:
        assert e.delta == parse_delta(delta)
    assert e.message == message


def test_event_creation_non_naive():
    with raises(ValueError, match='Must be a naive datetime'):
        Event('test', datetime(2013, 2, 26, 19, 45, 14, tzinfo=timezone.utc),
              None, None)


def test_event_equality():
    ev1 = Event('test', datetime(2013, 2, 26, 19, 45, 14), None, None)
    ev2 = Event('test', datetime(2013, 2, 26, 19, 45, 14), None, None)
    assert ev1 == ev2


@mark.parametrize('ev1, ev2', [
    (Event(
        'test',
        datetime(2013, 2, 26, 19, 45, 14),
    ), Event(
        'not_test',
        datetime(2013, 2, 26, 19, 45, 14),
    )),
    (Event(
        'date',
        datetime(2013, 2, 26, 19, 45, 14),
    ), Event(
        'date',
        datetime(2001, 1, 1, 0, 0, 0),
    )),
    (Event('message', datetime(2013, 2, 26, 19, 45, 14), None, 'test'),
     Event('message', datetime(2013, 2, 26, 19, 45, 14), None, 'breakage')),
])
def test_event_inequality(ev1: Event, ev2: Event):
    assert ev1 != ev2


@mark.parametrize('database, events', [
    ('test', 3),
    ('date_filtering', 3),
    ('test_not_running', 3),
])
def test_read_datebase(database: str, events: int):
    evs = Events.read('tests/data/' + database, write_cache=False)
    assert len(evs) == events


def test_read_invalid_data():
    with raises(ValueError, match='Invalid data'):
        Events.read('tests/data/faulty_csv', write_cache=False)


@mark.parametrize('database, events', [
    ('test', 3),
    ('date_filtering', 3),
    ('test_not_running', 3),
])
def test_read_datebase_wrapper(database: str, events: int):
    with Events.wrapping('tests/data/' + database, write_cache=False) as evs:
        assert len(evs) == events


def test_read_datebase_wrapper_write(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    with Events.wrapping(test_dir, write_cache=False) as evs:
        evs.stop()
    comp = dircmp('tests/data/test', test_dir, [])
    assert comp.diff_files == [
        'task.csv',
    ]
    assert comp.left_only == []
    assert comp.right_only == [
        'task.csv~',
    ]
    assert comp.funny_files == []
    assert comp.subdirs == {}


@mark.parametrize('database, result', [
    ('test', Event('task', '2011-05-04T09:30:00Z', '', 'finished')),
    ('', None),
])
def test_read_last(database: str, result: Optional[Event]):
    evs = Events.read('tests/data/' + database, write_cache=False)
    assert evs.last() == result


def test_fail_start_with_overlap():
    evs = Events.read('tests/data/test_not_running', write_cache=False)
    with raises(TaskRunningError, match='Start date overlaps'):
        evs.start('task', start=datetime(2011, 5, 4, 9, 33))


@mark.parametrize('n, task, start, delta', [
    (0, 'task', datetime(2011, 5, 4, 8), timedelta(hours=1)),
    (1, 'task2', datetime(2011, 5, 4, 9, 15), timedelta(minutes=15)),
    (2, 'task', datetime(2011, 5, 4, 9, 30), timedelta()),
])
def test_check_events(n: int, task: str, start: datetime, delta: timedelta):
    # FIXME: Clean-ish way to perform check, with the caveat that it parses the
    # database on each entry.  Need a better solution.
    events = Events.read('tests/data/test', write_cache=False)
    assert events[n].task == task
    assert events[n].start == start
    assert events[n].delta == delta


def test_write_database(tmpdir):
    in_dir = 'tests/data/test'
    events = Events.read(in_dir, write_cache=False)
    events._dirty = events.tasks()
    events.write(tmpdir.strpath)
    comp = dircmp(in_dir, tmpdir.strpath, [])
    assert comp.diff_files == []
    assert comp.left_only == []
    assert comp.right_only == []
    assert comp.funny_files == []
    assert comp.subdirs == {}


def test_write_database_event_backups(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    events = Events.read(test_dir, write_cache=False)
    events.start('task')
    events.write(test_dir)
    comp = dircmp('tests/data/test_not_running', test_dir, [])
    assert comp.diff_files == [
        'task.csv',
    ]
    assert comp.left_only == []
    assert comp.right_only == [
        'task.csv~',
    ]
    assert comp.funny_files == []
    assert comp.subdirs == {}


def test_write_database_no_change_noop(tmpdir):
    in_dir = 'tests/data/test'
    events = Events.read(in_dir, write_cache=False)
    events.write(tmpdir.strpath)
    assert glob(tmpdir.join('*').strpath) == []


def test_write_database_cache(temp_user_cache, tmpdir):
    events = Events.read('tests/data/test')
    events._dirty = events.tasks()
    events.write(tmpdir.join('database').strpath)
    cache_files = glob(
        tmpdir.join('cache', '**', '*.pkl').strpath, recursive=True)
    assert {f.split('/')[-1][:-4] for f in cache_files} == set(events.tasks())


def test_read_database_cache(temp_user_cache, monkeypatch):
    read = set()
    monkeypatch.setattr(events_mod.pickle, 'load',
                        lambda f: read.add(f.name.split('/')[-1][:-4]))
    in_dir = 'tests/data/test'
    events = Events.read(in_dir)
    events = Events.read(in_dir)
    assert read == set(events.tasks())


def test_read_database_cache_broken(temp_user_cache, tmpdir):
    in_dir = 'tests/data/test'
    events = Events.read(in_dir)
    cache_files = glob(
        tmpdir.join('cache', '**', '*.pkl').strpath, recursive=True)
    with open(cache_files[0], 'w') as f:
        f.write('Broken data')
    events2 = Events.read(in_dir)
    assert events == events2


def test_store_messages_with_events():
    events = Events.read('tests/data/test', write_cache=False)
    assert events.last().message == 'finished'


def test_non_existing_database():
    assert Events() == Events.read('I_NEVER_EXIST', write_cache=False)


@mark.skipif(
    not events_mod.cduration, reason='Skipping tests for cduration fallbacks')
def test_handling_of_cduration(monkeypatch):
    monkeypatch.setattr(events_mod, 'cduration', None)
    events = Events.read('tests/data/test', write_cache=False)
    assert events.last().message == 'finished'
