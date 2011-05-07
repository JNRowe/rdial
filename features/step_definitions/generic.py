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

from lettuce import world

import rdial

from util import step


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
    assert_equal(world.result, "")


@step(u'When I call %(IDENTIFIER)s on %(IDENTIFIER)s')
def when_i_call_method_on_obj(step, method, obj):
    try:
        getattr(getattr(world, obj), method)()
    except Exception as e:
        world.exception = e


@step(u'When I check %(IDENTIFIER)s attribute of %(IDENTIFIER)s')
def when_i_check_attribute(step, method, obj):
    world.result = unicode(getattr(getattr(world, obj), method))


@step(u'When I check output for calling %(IDENTIFIER)s on %(IDENTIFIER)s')
def when_i_check_output_for_calling_method(step, method, obj):
    world.result = unicode(getattr(getattr(world, obj), method)())


@step(u'When I call %(IDENTIFIER)s on %(IDENTIFIER)s with %(NAMED_PARAM)s')
def when_i_call_method_on_obj_with_args(step, method, obj, param, value):
    params = {str(param): value}
    try:
        getattr(getattr(world, obj), method)(**params)
    except Exception as e:
        world.exception = e


@step(u'When I check return value for calling %(IDENTIFIER)s on '
       '%(IDENTIFIER)s')
def when_i_check_retval_for_calling_method(step, method, obj):
    world.result = getattr(getattr(world, obj), method)()


@step(u'When I check return value for calling %(IDENTIFIER)s on '
       '%(IDENTIFIER)s with %(NAMED_PARAM)s%(OPT_PARAM)s%(OPT_PARAM)s')
def when_i_check_retval_for_calling_method_with_args(step, method, obj,
                                                     *params):
    used_params = filter(None, params)
    d = {}
    # Build dictionary with integer values, if possible
    for k, v in zip(used_params[0::2], used_params[1::2]):
        try:
            d[k] = int(v)
        except ValueError:
            d[k] = v
    world.result = getattr(getattr(world, obj), method)(**d)


@step(u'Then I receive %(IDENTIFIER)s')
def then_i_receive_exception(step, expected):
    assert_equal(unicode(world.exception.__class__.__name__), expected)
