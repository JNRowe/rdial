#
"""test_utils - Test utility functions"""
# Copyright © 2014-2016  James Rowe <jnrowe@gmail.com>
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

from os import listdir
from time import sleep

from click import open_file
from click.testing import CliRunner
from expecter import expect
from jnrbase.attrdict import AttrDict

from rdial.utils import (newer, read_config, remove_current, write_current)


def test_read_config_local():
    conf = read_config('tests/data/local.ini')
    expect(conf['local test'].as_bool('read')) == True


def test_handle_current():
    runner = CliRunner()
    with runner.isolated_filesystem() as tempdir:
        globs = AttrDict(directory=tempdir)
        bare = lambda globs, task: True
        write_current(bare)(globs, task='test')
        expect(listdir(tempdir)).contains('.current')
        remove_current(bare)(globs, task='test')
        expect(listdir(tempdir)).does_not_contain('.current')
        # check idempotent...
        remove_current(bare)(globs, task='test')


def test_newer():
    runner = CliRunner()
    with runner.isolated_filesystem() as tempdir:
        with open_file('%s/file1' % tempdir, 'w') as f1:
            sleep(0.1)
            with open_file('%s/file2' % tempdir, 'w') as f2:
                expect(newer(f2.name, f1.name)) == True
                expect(newer(f1.name, f2.name)) == False
                expect(newer(f1.name, f1.name)) == False
