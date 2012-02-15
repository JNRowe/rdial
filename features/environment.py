#
#
"""environment - Behave environment for rdial"""
# Copyright (C) 2011-2012  James Rowe <jnrowe@gmail.com>
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

import coverage


def before_all(context):
    """Set up coverage monitoring

    :param behave.runner.Context context: Behave execution context
    """
    context.coverage = coverage.coverage(branch=True, source=['rdial', ])
    context.coverage.start()


def after_all(context):
    """Finish and save coverage monitoring

    :param behave.runner.Context context: Behave execution context
    """
    context.coverage.stop()
    context.coverage.save()
