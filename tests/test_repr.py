#
"""test_repr - Test __repr__ methods for self-reproducibility."""
# Copyright © 2011-2019  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0+
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

from pytest import mark

from rdial.events import Event, Events


def eval_repr(obj: object):
    """Regenerate an object from its ``__repr__`` output.

    Args:
        obj: Object to evaluate

    """
    return repr(eval(repr(obj)))


@mark.parametrize('ev', [
    Event('task', '2011-05-05T11:23:48Z', 'PT01H00M00S'),
    Event('task', '2011-05-05T11:23:48Z', ''),
    Event('task', '2011-05-05T11:23:48Z', 'PT01H00M00S', 'message'),
])
def test_event_repr(ev: Event):
    assert repr(ev) == eval_repr(ev)


def test_events_repr():
    ev1 = Event('task', '2011-05-05T11:23:48Z', 'PT01H00M00S')
    ev2 = Event('task', '2011-05-05T12:23:48Z', 'PT00H30M00S')
    events = Events([ev1, ev2])
    assert repr(events) == eval_repr(events)
