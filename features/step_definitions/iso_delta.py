#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""iso_delta - Lettuce step functions for checking delta support"""
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

import datetime

from nose.tools import assert_equal

from lettuce import (step, world)


@step(u'Then I see the timedelta object (.*)')
def then_i_see_the_timedelta_object_result(step, expected):
    assert_equal(str(world.result), expected)


@step(u'Given I have the timedelta object (.*)')
def given_i_have_the_timedelta_object_timedelta(step, string):
    hours, minutes, seconds = map(int, string.split(":"))
    world.input = datetime.timedelta(hours=hours, minutes=minutes,
                                     seconds=seconds)
