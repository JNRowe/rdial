from nose.tools import assert_equal

from lettuce import (step, world)

import rdial


@step(u'Given I have the string (.*)')
def given_i_have_the_string_string(step, string):
    world.input = string


@step(u'When I process it with (.*)')
def when_i_process_it_with_function(step, function):
    world.result = getattr(rdial, function)(world.input)


@step(u'Then I see the string (.*)')
def then_i_see_the_string_result(step, expected):
    assert_equal(world.result, expected)
