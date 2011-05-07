#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""event - Lettuce step functions for checking event support"""
# Copyright (C) 2011  James Rowe <jnrowe@gmail.com>
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
import difflib
import os

from nose.tools import assert_equal

from lettuce import world

from util import step


PATH = os.path.dirname(os.path.abspath(__file__))


@step(u'Given I have the database (.*)')
def given_i_have_the_database_database(step, database):
    world.input = "%s/../data/%s" % (PATH, database)


@step(u'Then I see (\d+) events')
def then_i_see_n_events(step, expected):
    assert_equal(len(world.result), int(expected))


@step(u'Then I see event (\d+) contains (.*), (.*) and (.*)')
def then_i_see_event_n_contains_(step, event, project, start, delta):
    event = int(event)
    assert_equal(world.result[event].project, project)
    assert_equal(str(world.result[event].start), start)
    assert_equal(str(world.result[event].delta), delta)


@step(u'Given I have the events from (.*)')
def given_i_have_the_events_from_test_txt(step, database):
    step.given('I have the database %s' % database)
    step.given('I process it with Events.read')


@step(u'When I write it to a temp file')
def when_i_write_it_to_a_temp_file(step):
    file = "%s/../data/test_write.txt" % PATH
    world.file = file
    world.result.write(world.file)
    atexit.register(lambda: os.unlink(world.file))


@step(u'Then I see an duplicate of (.*)')
def then_i_see_an_duplicate_of_test_txt(step, file):
    def udiff(file1, file2):
        differ = difflib.unified_diff(open(file1).readlines(),
                                      open(file2).readlines(),
                                      file1, "test_output")
        return "".join(differ)
    file = "%s/../data/%s" % (PATH, file)
    diff_text = udiff(file, world.file)
    assert_equal(diff_text, "", "File comparison failed!\n" + diff_text)
