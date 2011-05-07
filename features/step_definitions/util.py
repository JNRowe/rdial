#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""util - Lettuce utility functions for rdial"""
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


from lettuce import step as lettuce_step


IDENTIFIER = u'([a-zA-Z_]\w*)'
NAMED_PARAM = u'([^=]+)=([^ ,]+)'
OPT_PARAM = u'(?:, ([^=]+)=([^ ,]+))?'


def step(match):
    """Replace values in match strings with constants from module

    The purpose is entirely to improve the look and readability of the steps
    defined below, it provides nothing over hard coding the values in step
    definitions.
    """
    consts = dict(filter(lambda e: e[0].upper() == e[0], globals().items()))
    return lettuce_step("%s$" % match % consts)
