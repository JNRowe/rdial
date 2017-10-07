#
"""test_repr - Test __repr__ methods for self-reproducibility"""
# Copyright © 2011-2016  James Rowe <jnrowe@gmail.com>
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

import unittest

from rdial.events import Event, Events


def eval_repr(obj):
    """Regenerate an object from its __repr__ output.

    Args:
        obj (object): Object to evaluate

    """
    return repr(eval(repr(obj)))


class ReprTest(unittest.TestCase):

    """repr() should return self-documenting string."""

    def test_event(self):
        ev = Event('task', '2011-05-05T11:23:48Z', 'PT01H00M00S')
        assert repr(ev) == eval_repr(ev)

    def test_event_no_delta(self):
        ev = Event('task', '2011-05-05T11:23:48Z', '')
        assert repr(ev) == eval_repr(ev)

    def test_event_with_message(self):
        ev = Event('task', '2011-05-05T11:23:48Z', 'PT01H00M00S', 'message')
        assert repr(ev) == eval_repr(ev)

    def test_events(self):
        ev1 = Event('task', '2011-05-05T11:23:48Z', 'PT01H00M00S')
        ev2 = Event('task', '2011-05-05T12:23:48Z', 'PT00H30M00S')
        events = Events([ev1, ev2])
        assert repr(events) == eval_repr(events)
