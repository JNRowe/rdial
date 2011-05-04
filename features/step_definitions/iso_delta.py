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
