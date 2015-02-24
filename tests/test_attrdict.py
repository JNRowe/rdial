#
# coding=utf-8
"""test_attrdict - Test AttrDict support"""
# Copyright © 2011-2015  James Rowe <jnrowe@gmail.com>
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

from rdial.utils import AttrDict


class AttrDictTest(TestCase):
    def setUp(self):
        self.ad = AttrDict(carrots=3, snacks=0)

    def test_base(self):
        self.ad.must.be.a(dict)

        self.ad['carrots'].must.equal(3)
        self.ad['snacks'].must.equal(0)

        sorted(self.ad.keys()).must.equal(['carrots', 'snacks'])

    def test___contains__(self):
        self.ad.must.contain('carrots')
        self.ad.does_not.contain('prizes')

    def test___getattr__(self):
        self.ad.carrots.must.equal(3)
        self.ad.snacks.must.equal(0)

    def test___setattr__(self):
        self.ad.carrots, self.ad.snacks = 0, 3
        self.ad.carrots.must.equal(0)
        self.ad.snacks.must.equal(3)

    def test___delattr__(self):
        self.ad.must.contain('carrots')
        del self.ad['carrots']
        self.ad.does_not.contain('carrots')
