#
# coding=utf-8
"""test_utils - Test utility functions"""
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

from os import listdir
from subprocess import CalledProcessError
try:
    from tempfile import TemporaryDirectory
except ImportError:  # Python 2
    from shutil import rmtree
    from tempfile import mkdtemp
from time import sleep

from expecter import expect
from mock import patch

from rdial.compat import PY2
from rdial.utils import (AttrDict, check_output, newer, read_config,
                         remove_current, write_current)


def test_check_output():
    expect(check_output(['echo', 'hello'])) == 'hello\n'


def test_check_output_py26_compat():
    with patch('subprocess.check_output', side_effect=AttributeError):
        expect(check_output(['echo', 'hello'])) == 'hello\n'


def test_check_output_py26_compat_fail():
    with patch('subprocess.check_output', side_effect=AttributeError):
        with expect.raises(CalledProcessError):
            check_output(['false', ])


def test_read_config_local():
    conf = read_config('tests/data/local.ini')
    expect(conf['local test'].as_bool('read')) == True


def test_handle_current():
    if PY2:
        try:
            tmpdir = mkdtemp()
            globs = AttrDict(directory=tmpdir)
            bare = lambda globs, task: True
            write_current(bare)(globs, task='test')
            expect(listdir(tmpdir)).contains('.current')
            remove_current(bare)(globs, task='test')
            expect(listdir(tmpdir)).does_not_contain('.current')
            # check idempotent...
            remove_current(bare)(globs, task='test')
        finally:
            rmtree(tmpdir)
    else:
        with TemporaryDirectory() as tmpdir:
            globs = AttrDict(directory=tmpdir.name)
            bare = lambda globs, task: True
            write_current(bare)(globs, task='test')
            expect(listdir(tmpdir)).contains('.current')
            remove_current(bare)(globs, task='test')
            expect(listdir(tmpdir)).does_not_contain('.current')
            # check idempotent...
            remove_current(bare)(globs, task='test')


def test_newer():
    if PY2:
        try:
            tmpdir = mkdtemp()
            f1 = open('%s/file1' % tmpdir, 'w')
            sleep(0.1)
            f2 = open('%s/file2' % tmpdir, 'w')
            expect(newer(f2.name, f1.name)) == True
            expect(newer(f1.name, f2.name)) == False
            expect(newer(f1.name, f1.name)) == False
        finally:
            rmtree(tmpdir)
    else:
        with TemporaryDirectory() as tmpdir:
            f1 = open('%s/file1' % tmpdir.name, 'w')
            sleep(0.1)
            f2 = open('%s/file2' % tmpdir.name, 'w')
            expect(newer(f2.name, f1.name)) == True
            expect(newer(f1.name, f2.name)) == False
            expect(newer(f1.name, f1.name)) == False
