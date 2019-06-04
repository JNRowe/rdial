#
"""test_utils - Test utility functions."""
# Copyright © 2014-2019  James Rowe <jnrowe@gmail.com>
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

from time import sleep
from typing import Dict, Optional

from jnrbase.attrdict import ROAttrDict
from pytest import mark

from rdial.utils import (newer, read_config, remove_current, term_link,
                         write_current)


def test_read_config_local():
    conf = read_config('tests/data/local.ini')
    assert conf['local test'].getboolean('read')


@mark.parametrize('config, options, result', [
    (None, None, False),
    ('tests/data/stacking.ini', None, True),
    ('tests/data/stacking.ini', {
        'interactive': False
    }, False),
])
def test_read_config_stacking(config: Optional[str],
                              options: Optional[Dict[str, bool]],
                              result: bool):
    conf = read_config(config, options)
    assert conf['rdial'].getboolean('interactive') is result


def test_handle_current(tmpdir):
    globs = ROAttrDict(directory=tmpdir.strpath)
    bare = lambda globs, task: True
    write_current(bare)(globs, task='test')
    assert tmpdir.join('.current').exists()
    remove_current(bare)(globs, task='test')
    assert not tmpdir.join('.current').exists()
    # check idempotent…
    remove_current(bare)(globs, task='test')


def test_newer(tmpdir):
    f1 = tmpdir.join('file1').ensure()
    sleep(0.1)
    f2 = tmpdir.join('file2').ensure()
    assert newer(f2.strpath, f1.strpath)
    assert not newer(f1.strpath, f2.strpath)
    assert not newer(f1.strpath, f1.strpath)


@mark.parametrize('target, name, result', [
    ('pypi://rdial', 'this package',
     '\x1b]8;;pypi://rdial\x07this package\x1b]8;;\x07'),
    ('pypi://rdial', None, '\x1b]8;;pypi://rdial\x07rdial\x1b]8;;\x07'),
])
def test_term_link(target: str, name: Optional[str], result: str):
    assert term_link(target, name) == result
