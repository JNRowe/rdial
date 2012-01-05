#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""util - Behave utility functions for rdial"""
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


from behave import given as behave_given
from behave import then as behave_then
from behave import when as behave_when


REPLACEMENTS = {
    'IDENTIFIER': u'([a-zA-Z_]\w*)',
    'NON_GROUPING_IDENTIFIER': u'(?:[a-zA-Z_]\w*)',
    'NAMED_PARAM': u'([^=]+)=([^ ,]+)',
    'OPT_PARAM': u'(?:, ([^=]+)=([^ ,]+))?',
}


def step(f):
    """Replace values in match strings with constants from module

    This is only used to improve the look and readability of steps with large
    regular expressions, it provides nothing else over hard coding the values
    in step definitions.
    """
    return lambda match: f("%s" % match % REPLACEMENTS)

given = step(behave_given)
then = step(behave_then)
when = step(behave_when)


def param_dict(params):
    """Generate a dictionary from parameter list

    Parameters are expected to be in repeating ``key, value`` pairs.

    All ``None`` keys and their associated values(regardless of content) are
    scrubbed, to make it easier to reuse steps.

    Values are converted to ``int`` if possible.

    :param list params: List of parameters
    :return dict: Dictionary of parameters
    """
    d = {}
    # Build dictionary with integer values, if possible
    for k, v in zip(params[0::2], params[1::2]):
        if k is None:
            continue
        try:
            d[str(k)] = int(v)
        except ValueError:
            d[str(k)] = v
    return d
