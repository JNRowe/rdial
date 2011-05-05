#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""generic - Generic Lettuce step functions"""
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

from nose.tools import assert_equal

from lettuce import (step, world)

import rdial


@step(u'Given I have the string (.*)')
def given_i_have_the_string_string(step, string):
    world.input = string


@step(u'Given I have an empty string')
def given_i_have_an_empty_string(step):
    world.input = ""


@step(u'When I process it with ([^\.]+)$')
def when_i_process_it_with_function(step, function):
    world.result = getattr(rdial, function)(world.input)


@step(u'When I process it with ([^\.]+)\.([^\.]+)$')
def when_i_process_it_with_method(step, obj, method):
    world.result = getattr(getattr(rdial, obj), method)(world.input)


@step(u'Then I see the string (.*)')
def then_i_see_the_string_result(step, expected):
    assert_equal(world.result, expected)


@step(u'Then I see an empty string')
def then_i_see_an_empty_string(step):
    assert_equal(world.result, "")
