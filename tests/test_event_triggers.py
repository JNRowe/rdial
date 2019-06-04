#
"""test_event_triggers - Test event trigger handling."""
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

from pytest import raises

from rdial.events import (Events, TaskNotExistError, TaskNotRunningError,
                          TaskRunningError)


def test_start_event():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    events.start('task2')
    assert events.running() == 'task2'


def test_fail_start_when_task_typo():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    with raises(
            TaskNotExistError,
            match='Task non_existent does not exist!  Use “--new” to '
            'create it'):
        events.start('non_existent')


def test_fail_start_when_running():
    events = Events.read('tests/data/test', write_cache=False)
    with raises(TaskRunningError, match='Running task task!'):
        events.start('task2')


def test_stop_event():
    events = Events.read('tests/data/test', write_cache=False)
    events.stop()
    assert not events.running()


def test_stop_event_with_message():
    events = Events.read('tests/data/test', write_cache=False)
    events.stop(message='test')
    last = events.last()
    assert last.message == 'test'


def test_fail_stop_when_not_running():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    with raises(TaskNotRunningError, match='No task running!'):
        events.stop()


def test_fail_stop_single_when_not_running():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    with raises(TaskNotRunningError, match='No task running!'):
        events.last().stop()
