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

from lettuce import (after, before, world)

import rdial

from util import (param_dict, step)


@before.all
def intro():
    print 'These tests should all run successfully with Python 2.5-2.7,'
    print 'if you receive errors please report a bug!'


@after.all
def outro(total):
    if not total.scenarios_ran == total.scenarios_passed:
        print
        print "Whoops, you'll be wanting the bug report address then:"
        print '    https://github.com/JNRowe/rdial/issues'
        print


@step(u'Given I have the string ["\']?(.*?)["\']?')
def given_i_have_the_string_string(step, string):
    world.input = string


@step(u'Given I have an empty string')
def given_i_have_an_empty_string(step):
    world.input = ""


@step(u'When I process it with %(IDENTIFIER)s')
def when_i_process_it_with_function(step, function):
    world.result = getattr(rdial, function)(world.input)


@step(u'When I process it with %(IDENTIFIER)s\.%(IDENTIFIER)s')
def when_i_process_it_with_method(step, obj, method):
    world.result = getattr(getattr(rdial, obj), method)(world.input)


@step(u'Then I see the string ["\']?(.*?)["\']?')
def then_i_see_the_string_result(step, expected):
    assert_equal(world.result, expected)


@step(u'Then I see an empty string')
def then_i_see_an_empty_string(step):
    step.given('Then I see the string ""')


@step(u'When I call %(IDENTIFIER)s on %(IDENTIFIER)s')
def when_i_call_method_on_obj(step, method, obj):
    step.given(u'When I call %s on %s without args' % (method, obj))


@step(u'When I check %(IDENTIFIER)s attribute of %(IDENTIFIER)s')
def when_i_check_attribute(step, attribute, obj):
    world.result = unicode(getattr(getattr(world, obj), attribute))


@step(u'When I check output for calling %(IDENTIFIER)s on %(IDENTIFIER)s')
def when_i_check_output_for_calling_method(step, method, obj):
    world.result = unicode(getattr(getattr(world, obj), method)())


@step(u'When I call %(IDENTIFIER)s on %(IDENTIFIER)s '
       '(?:with %(NAMED_PARAM)s|without args)')
def when_i_call_method_on_obj_with_args(step, method, obj, *params):
    params = param_dict(params)
    try:
        getattr(getattr(world, obj), method)(**params)
    except (Exception, ), e:
        world.exception = e


@step(u'When I check return value for calling %(IDENTIFIER)s on '
       '%(IDENTIFIER)s')
def when_i_check_retval_for_calling_method(step, method, obj):
    step.given(u'When I check return value for calling %s on %s without args'
        % (method, obj))


@step(u'When I check return value for calling %(IDENTIFIER)s on %(IDENTIFIER)s'
       ' (?:with %(NAMED_PARAM)s%(OPT_PARAM)s%(OPT_PARAM)s|without args)')
def when_i_check_retval_for_calling_method_with_args(step, method, obj,
                                                     *params):
    params = param_dict(params)
    world.result = getattr(getattr(world, obj), method)(**params)


@step(u'Then I receive %(IDENTIFIER)s')
def then_i_receive_exception(step, expected):
    world.result = world.exception.__class__.__name__
    step.given('Then I see the string "%s"' % expected)


@step(u'Then I see the %(NON_GROUPING_IDENTIFIER)s object (.*)')
def then_i_see_the_identifier_object_result(step, expected):
    world.result = unicode(world.result)
    step.given('Then I see the string "%s"' % expected)
