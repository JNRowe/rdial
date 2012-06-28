#
#
"""generic - Generic Behave step functions"""
# Copyright (C) 2011-2012  James Rowe <jnrowe@gmail.com>
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

from expecter import expect

from behave import step_matcher

import rdial

from util import (given, param_dict, then, when)


@given('I have an empty string')
def g_have_empty_string(context):
    context.input = ""


@then('I see an empty string')
def t_see_empty_string(context):
    context.execute_steps(u'Then I see the string ""')


@then('I receive {error}')
def t_receive_exception(context, error):
    context.result = context.exception.__class__.__name__
    context.execute_steps('Then I see the string "%s"' % error)


step_matcher('re')


@given('I have the string ["\']?(.*?)["\']?$')
def g_have_string(context, string):
    context.input = string


@when('I process it with %(IDENTIFIER)s')
def w_process_with_function(context, function):
    context.result = getattr(rdial, function)(context.input)


@when('I apply the %(IDENTIFIER)s\.%(IDENTIFIER)s method')
def w_process_with_method(context, obj, method):
    context.result = getattr(getattr(rdial, obj), method)(context.input)


@then('I see the string ["\']?(.*?)["\']?$')
def t_see_string(context, result):
    expect(context.result) == result


@when('I call %(IDENTIFIER)s on %(IDENTIFIER)s$')
def w_call_obj_method(context, method, obj):
    context.execute_steps('When I call %s on %s without args' % (method, obj))


@when('I check %(IDENTIFIER)s attribute of %(IDENTIFIER)s')
def w_check_attribute(context, attribute, obj):
    context.result = unicode(getattr(getattr(context, obj), attribute))


@when('I check output for calling %(IDENTIFIER)s on %(IDENTIFIER)s')
def w_method_output(context, method, obj):
    context.result = unicode(getattr(getattr(context, obj), method)())


@when('I call %(IDENTIFIER)s on %(IDENTIFIER)s '
      '(?:with %(NAMED_PARAM)s|without args)')
def w_call_obj_method_args(context, method, obj, *params):
    params = param_dict(params)
    try:
        getattr(getattr(context, obj), method)(**params)
    except (Exception, ), e:
        context.exception = e


@when('I check return value for calling %(IDENTIFIER)s on %(IDENTIFIER)s$')
def w_check_method_retval(context, method, obj):
    context.result = getattr(getattr(context, obj), method)()


def call_with_args(context, method, obj, *params):
    params = param_dict(params)
    context.result = getattr(getattr(context, obj), method)(**params)


@when('I check return value for calling %(IDENTIFIER)s on %(IDENTIFIER)s'
      ' with %(NAMED_PARAM)s$')
def w_check_method_retval_one_arg(context, method, obj, *params):
    call_with_args(context, method, obj, *params)


@when('I check return value for calling %(IDENTIFIER)s on %(IDENTIFIER)s'
      ' with %(NAMED_PARAM)s and %(NAMED_PARAM)s$')
def w_check_method_retval_two_args(context, method, obj, *params):
    call_with_args(context, method, obj, *params)


@when('I check return value for calling %(IDENTIFIER)s on %(IDENTIFIER)s'
      ' with %(NAMED_PARAM)s, %(NAMED_PARAM)s and %(NAMED_PARAM)s$')
def w_check_method_retval_three_args(context, method, obj, *params):
    call_with_args(context, method, obj, *params)


@then('I see the %(NON_GROUPING_IDENTIFIER)s object (.*)')
def t_see_object_result(context, result):
    context.result = unicode(context.result)
    context.execute_steps('Then I see the string "%s"' % result)

step_matcher('parse')
