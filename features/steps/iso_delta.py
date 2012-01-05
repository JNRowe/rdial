#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""iso_delta - Behave step functions for checking delta support"""
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

from behave import given


@given('I have the timedelta object {string}')
def g_have_timedelta(context, string):
    if ', ' in string:
        days, time = string.split(", ")
        days = int(days.split(" ")[0])
    else:
        days = 0
        time = string
    hours, minutes, seconds = map(int, time.split(":"))
    context.input = datetime.timedelta(days=days, hours=hours, minutes=minutes,
                                       seconds=seconds)
