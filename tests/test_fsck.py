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

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # NOQA

from expecter import expect
from mock import patch

from rdial.cmdline import cli


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.exit', new=lambda x: True)
def test_fsck_overlap(stdout):
    cli.main(args=['--directory=tests/data/test_fsck', 'fsck'])
    expect(stdout.getvalue()).contains('Overlap')
    expect(stdout.getvalue()).contains("'2011-05-04T09:15:00Z', 'PT35M'")
