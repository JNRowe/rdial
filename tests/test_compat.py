#
# coding=utf-8
"""test_compat - Test Python 2/3 compatibility support"""
# Copyright © 2016  James Rowe <jnrowe@gmail.com>
#
# This file is part of rdial.
#
# rdial is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# rdial is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# rdial.  If not, see <http://www.gnu.org/licenses/>.

from expecter import expect

from rdial.compat import (PY2, mangle_repr_type)


def test_unicode_repr():
    @mangle_repr_type
    class Test:

        def __repr__(self):
            return 'test'
    repr_string = repr(Test())
    if PY2:
        expect(repr_string) == u'test'
    else:
        expect(repr_string) == 'test'
