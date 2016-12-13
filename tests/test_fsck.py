#
# coding=utf-8
"""test_fsck - Test database fsck support"""
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

from datetime import datetime

from click.testing import CliRunner
from expecter import expect
from hiro import Timeline

from rdial.cmdline import cli


def test_fsck_overlap():
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory=tests/data/test_fsck',
                                 '--no-cache', 'fsck'])
    expect(result.exit_code) == 1
    expect(result.output).contains('Overlap')
    expect(result.output).contains("'2011-05-04T09:15:00Z', 'PT35M'")


@Timeline(start=datetime(2016, 12, 13, 23, 0))
def test_fsck_future_start(timeline):
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory=tests/data/test_fsck_future',
                                 '--no-cache', 'fsck'])
    expect(result.exit_code) == 1
    expect(result.output).contains('Future start')


@Timeline(start=datetime(2016, 12, 13, 23, 7))
def test_fsck_future_end(timeline):
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory=tests/data/test_fsck_future',
                                 '--no-cache', 'fsck'])
    expect(result.exit_code) == 1
    expect(result.output).contains('Future end')
