#
#
"""iso_delta - Behave step functions for checking delta support"""
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

import datetime

from behave import given


@given('I have the timedelta object {days:d} days,'
       ' {hours:d}:{minutes:d}:{seconds:d}')
def g_have_timedelta_with_days(context, days, hours, minutes, seconds):
    context.input = datetime.timedelta(days=days, hours=hours, minutes=minutes,
                                       seconds=seconds)


@given('I have the timedelta object {hours:d}:{minutes:d}:{seconds:d}')
def g_have_timedelta(context, hours, minutes, seconds):
    context.input = datetime.timedelta(hours=hours, minutes=minutes,
                                       seconds=seconds)
