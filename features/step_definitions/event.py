import atexit
import hashlib
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
    file = "%s/../data/%s" % (PATH, file)
    hash_file = lambda x: hashlib.sha1(open(x).read()).hexdigest()
    assert_equal(hash_file(world.file), hash_file(file),
                 "Hash of file content doesn't match!")
