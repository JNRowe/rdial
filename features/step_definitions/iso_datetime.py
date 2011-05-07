#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""iso_datetime - Lettuce step functions for checking datetime support"""
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

import isodate

from nose.tools import assert_equal

from lettuce import world

from util import step


@step(u'Then I see the datetime object (.*)')
def then_i_see_the_datetime_object_result(step, expected):
    assert_equal(str(world.result), expected)


@step(u'Given I have the datetime object (.*)')
def given_i_have_the_datetime_object_datetime(step, string):
    datetime_ = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    world.input = datetime_.replace(tzinfo=isodate.UTC)
