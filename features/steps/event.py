#
#
"""event - Behave step functions for checking event support"""
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

import atexit
import os

from difflib import unified_diff
from glob import glob

from behave import (given, then, when)

from nose.tools import assert_equal


@given('I have the database {database}')
def g_have_database(context, database):
    context.input = "features/data/%s" % database


@then('I see {events:d} events')
def t_see_events(context, events):
    assert_equal(len(context.result), events)


@then('I see event {event:d} contains {task}, {start} and {delta}')
def t_see_event_contains(context, event, task, start, delta):
    assert_equal(context.result[event].task, task)
    assert_equal(str(context.result[event].start), start)
    assert_equal(str(context.result[event].delta), delta)


@given('I have the events from {database}')
def g_have_events_database(context, database):
    context.execute_steps('''
        Given I have the database %s
        When I apply the Events.read method
    ''' % database)


@when('I write it to a temp directory')
def w_write_temp(context):
    context.directory = "features/data/test_write"
    context.result.write(context.directory)


@then('I see an duplicate of {directory}')
def t_see_duplicate(context, directory):
    def remove_temp(directory):
        for i in os.listdir(directory):
            os.unlink('%s/%s' % (directory, i))
        os.rmdir(directory)
    atexit.register(remove_temp, context.directory)

    def udiff(file1, file2):
        differ = unified_diff(open(file1).readlines(), open(file2).readlines(),
                              file1, "test_output")
        return "".join(differ)
    old_files = sorted(glob("features/data/%s/*.csv" % directory))
    new_files = sorted(glob("%s/*.csv" % context.directory))
    diff_text = []
    for old, new in zip(old_files, new_files):
        diff_text.extend(udiff(old, new))
    diff_text = "\n".join(diff_text)
    assert_equal(diff_text, "", "File comparison failed!\n" + diff_text)
