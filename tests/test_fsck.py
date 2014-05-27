#
# coding=utf-8
"""test_fsck - Test database fsck support"""
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

from click.testing import CliRunner
from expecter import expect

from rdial.cmdline import cli


def test_fsck_overlap():
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory=tests/data/test_fsck', 'fsck'])
    expect(result.exit_code) == 0
    expect(result.output).contains('Overlap')
    expect(result.output).contains("'2011-05-04T09:15:00Z', 'PT35M'")
