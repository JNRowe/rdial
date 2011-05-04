import os

from nose.tools import assert_equal

from lettuce import (step, world)

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
