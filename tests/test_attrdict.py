#
# coding=utf-8
"""test_attrdict - Test AttrDict support"""
# Copyright © 2011-2014  James Rowe <jnrowe@gmail.com>
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

from unittest import TestCase

from expecter import expect

from rdial.utils import AttrDict


class AttrDictTest(TestCase):
    def setUp(self):
        self.ad = AttrDict(carrots=3, snacks=0)

    def test_base(self):
        expect(self.ad).isinstance(dict)

        expect(self.ad['carrots']) == 3
        expect(self.ad['snacks']) == 0

        expect(sorted(self.ad.keys())) == ['carrots', 'snacks']

    def test___contains__(self):
        expect(self.ad).contains('carrots')
        expect(self.ad).does_not_contain('prizes')

    def test___getattr__(self):
        expect(self.ad.carrots) == 3
        expect(self.ad.snacks) == 0

    def test___setattr__(self):
        self.ad.carrots, self.ad.snacks = 0, 3
        expect(self.ad.carrots) == 0
        expect(self.ad.snacks) == 3

    def test___delattr__(self):
        expect(self.ad).contains('carrots')
        del self.ad['carrots']
        expect(self.ad).does_not_contain('carrots')
