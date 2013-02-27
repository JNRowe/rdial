#
# coding=utf-8
"""base - CLI parsers for rdial"""
# Copyright © 2012, 2013  James Rowe <jnrowe@gmail.com>
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

import argparse
import datetime
import os

from rdial.i18n import _


# pylint: disable-msg=R0903
class TaskAction(argparse.Action):

    """Define task name, handling --from-dir option."""

    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.task is True:
            namespace.task = os.path.basename(os.path.abspath(os.curdir))
        else:
            namespace.task = values
# pylint: enable-msg=R0903


def task_name_typecheck(string):
    """Check given task name is valid.

    :param str string: Task name to check
    :rtype: :obj:`str`
    :returns: Task name, if valid
    :raises argparse.ArgparseTypeError: If task name is invalid

    """
    if string.startswith('.') or '/' in string or '\000' in string:
        raise argparse.ArgumentTypeError(_('%r is not a valid task name')
                                         % string)
    return string


# pylint: disable-msg=C0103
task_parser = argparse.ArgumentParser(add_help=False)
names_group = task_parser.add_mutually_exclusive_group()
names_group.add_argument('-x', '--from-dir', action='store_true', dest='task',
                         help=_('use directory name as task'))
names_group.add_argument('task', default='default', nargs='?',
                         action=TaskAction, help=_('task name'),
                         type=task_name_typecheck)

duration_parser = argparse.ArgumentParser(add_help=False)
duration_parser.add_argument('-d', '--duration', default='all',
                             choices=['day', 'week', 'month', 'year', 'all'],
                             help=_("filter events for specified time period"))
# pylint: enable-msg=C0103


def filter_events(events, task=None, duration=None):
    """Filter events for report processing.

    :param Events Events: Events to operate on
    :param str task: Task name to filter on
    :param str duration: Time window to filter on
    :rtype: :obj:`rdial.events.Events`
    :return: Events matching specified criteria

    """
    if task:
        events = events.for_task(task)
    if not duration == "all":
        if duration == "week":
            today = datetime.date.today()
            events = events.for_week(*today.isocalendar()[:2])
        else:
            year, month, day = datetime.date.today().timetuple()[:3]
            if duration == "month":
                day = None
            elif duration == "year":
                month = None
                day = None
            events = events.for_date(year, month, day)
    return events
