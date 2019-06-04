#
"""test_fsck - Test database fsck support."""
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

from datetime import datetime

from click.testing import CliRunner
from hiro import Timeline
from pytest import mark

from rdial.cmdline import cli


def test_fsck_clean():
    runner = CliRunner()
    result = runner.invoke(cli, '--directory=tests/data/test --no-cache fsck')
    assert result.exit_code == 0
    assert result.stdout.strip() == ''


@mark.parametrize('progress', ['--progress', '--no-progress'])
def test_fsck_overlap(progress: str):
    runner = CliRunner()
    result = runner.invoke(
        cli, f'--directory=tests/data/test_fsck --no-cache fsck {progress}')
    assert result.exit_code == 1
    assert 'Overlap' in result.stdout
    assert "'2011-05-04T09:15:00Z', 'PT35M'" in result.stdout


def test_fsck_future_start():
    with Timeline(start=datetime(2016, 12, 13, 23, 0)):
        runner = CliRunner()
        result = runner.invoke(
            cli, '--directory=tests/data/test_fsck_future --no-cache fsck')
    assert result.exit_code == 1
    assert 'Future start' in result.stdout


def test_fsck_future_end():
    with Timeline(start=datetime(2016, 12, 13, 23, 7)):
        runner = CliRunner()
        result = runner.invoke(
            cli, '--directory=tests/data/test_fsck_future --no-cache fsck')
    assert result.exit_code == 1
    assert 'Future end' in result.stdout
