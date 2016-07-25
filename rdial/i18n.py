#
# coding=utf-8
"""i18n - Internationalisation support for rdial."""
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

from __future__ import absolute_import

import gettext
import locale

from os import path

from .compat import PY2

locale.setlocale(locale.LC_ALL, '')

kwargs = {
    'localedir': path.join(path.realpath(path.dirname(__file__)), 'locale'),
    'names': ['gettext', 'ngettext', ]
}
if PY2:
    kwargs['unicode'] = 1

gettext.install('rdial', **kwargs)

_, N_ = _, ngettext  # NOQA: bindings from gettext.install above

__all__ = (_, N_)
