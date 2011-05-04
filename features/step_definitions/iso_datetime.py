import datetime

from nose.tools import assert_equal

from lettuce import (step, world)


@step(u'Then I see the datetime object (.*)')
def then_i_see_the_datetime_object_result(step, expected):
    assert_equal(str(world.result), expected)


@step(u'Given I have the datetime object (.*)')
def given_i_have_the_datetime_object_datetime(step, string):
    world.input = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
