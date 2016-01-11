#
# coding=utf-8
"""test_event_triggers - Test event trigger handling"""
# Copyright © 2012-2016  James Rowe <jnrowe@gmail.com>
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


from expecter import expect

from rdial.events import (Events, TaskNotExistError, TaskNotRunningError,
                          TaskRunningError)


def test_start_event():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    events.start(task='task2')
    expect(events.running()) == 'task2'


def test_fail_start_when_task_typo():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    with expect.raises(TaskNotExistError,
                       "Task non_existant does not exist!  Use `--new' to "
                       'create it'):
        events.start(task='non_existant')


def test_fail_start_when_running():
    events = Events.read('tests/data/test', write_cache=False)
    with expect.raises(TaskRunningError, 'Running task task!'):
        events.start(task='task2')


def test_stop_event():
    events = Events.read('tests/data/test', write_cache=False)
    events.stop()
    expect(events.running()) == False


def test_stop_event_with_message():
    events = Events.read('tests/data/test', write_cache=False)
    events.stop(message='test')
    last = events.last()
    expect(last.message) == 'test'


def test_fail_stop_when_not_running():
    events = Events.read('tests/data/test_not_running', write_cache=False)
    with expect.raises(TaskNotRunningError, 'No task running!'):
        events.stop()
