#! /usr/bin/env python3
"""timew_import - Import functionality for rdial."""
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
from csv import writer
from datetime import timedelta
from json import load
from os import makedirs, path
from typing import Dict, List, TextIO

from ciso8601 import parse_datetime
from click import BadOptionUsage, File, Path, argument, command
from click.utils import LazyFile
from jnrbase.attrdict import AttrDict
from jnrbase.colourise import pwarn
from jnrbase.iso_8601 import format_datetime, format_delta

from rdial.events import FIELDS, RdialDialect


def munge(dct: Dict) -> AttrDict:
    dct = AttrDict(**dct)
    if 'start' in dct:
        dct.start = parse_datetime(dct.start)
    if 'end' in dct:
        dct.end = parse_datetime(dct.end)
    return dct


def process_records(location: TextIO) -> Dict[str, List[str]]:
    data = load(location, object_hook=munge)
    tag_warning = False
    files = defaultdict(list)
    for ev in data:
        if len(ev.tags) > 1 and not tag_warning:
            pwarn('Multiple tags are not supported, using first')
            tag_warning = True
        if 'end' in ev:
            ev.end = ev.end - ev.start
        else:
            ev.end = timedelta(0)
        files[ev.tags[0]].append(
            [format_datetime(ev.start),
             format_delta(ev.end), None])
    return files


def write_events(location: str, files: Dict[str, List[str]]) -> None:
    makedirs(location)
    for fn, data in files.items():
        with LazyFile(f'{location}/{fn}.csv', 'w', atomic=True) as temp:
            w = writer(temp, dialect=RdialDialect)
            w.writerow(FIELDS)
            for ev in data:
                w.writerow(ev)


@command(
    epilog=('Please report bugs at '
            'https://github.com/JNRowe/rdial/issues'),
    context_settings={'help_option_names': ['-h', '--help']})
@argument('input', type=File())
@argument('output', type=Path(exists=False))
def main(input: TextIO, output: str) -> None:
    """Export timew data for use with rdial.

    Reads the output of ‘timew export’, and writes rdial compatible data to
    ‘output’.
    """
    if path.exists(output):
        raise BadOptionUsage('output', 'Output path must not exist')
    files = process_records(input)
    write_events(output, files)


if __name__ == '__main__':
    main()
