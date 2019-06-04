#! /usr/bin/env python3
"""timew_export - Export functionality for rdial."""
# Copyright © 2018  James Rowe <jnrowe@gmail.com>
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

from collections import defaultdict
from os import makedirs
from os.path import exists
from typing import Dict, List

from click import BadOptionUsage, Path, argument, command, open_file, option
from jnrbase.colourise import pwarn
from jnrbase.xdg_basedir import user_data

from rdial.events import Events


def process_events(location: str) -> Dict[str, List[str]]:
    with Events.wrapping(location, write_cache=False) as evs:
        task_warning = False
        message_warning = False
        files = defaultdict(list)
        for ev in evs:
            if '-' in ev.task:
                task = ev.task.replace('-', '_')
                if not task_warning:
                    pwarn('Task names containing ‘-’ will use ‘_’ in export')
                task_warning = True
            else:
                task = ev.task
            if ev.message and not message_warning:
                pwarn('Event messages aren’t supported by timew')
                message_warning = True
            out = [
                f'inc {ev.start:%Y%m%dT%H%M%SZ}',
            ]
            if ev.delta:
                out.append(f'- {ev.start + ev.delta:%Y%m%dT%H%M%SZ}')
            out.append(f'# {task}\n')
            files[ev.start.strftime('%Y-%m')].append(' '.join(out))
    return files


def write_events(location: str, files: Dict[str, List[str]]) -> None:
    makedirs(location)
    for fn, data in files.items():
        with open_file(f'{location}/{fn}.data', 'w', atomic=True) as f:
            f.writelines(data)


@command(
    epilog=('Please report bugs at '
            'https://github.com/JNRowe/rdial/issues'),
    context_settings={'help_option_names': ['-h', '--help']})
@option(
    '--database',
    default=user_data('rdial'),
    type=Path(exists=True, file_okay=False),
    help='Path to rdial database')
@argument('output', type=Path(exists=False))
def main(database: str, output: str) -> None:
    """Export rdial data for use with timew.

    Writes timew compatible data to ‘output’.
    """
    if exists(output):
        raise BadOptionUsage('output', 'Output path must not exist')
    files = process_events(database)
    write_events(output, files)


if __name__ == '__main__':
    main()
