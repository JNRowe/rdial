#! /usr/bin/env python3
"""setup.py - Setuptools tasks and config for rdial."""
# Copyright © 2011-2018  James Rowe <jnrowe@gmail.com>
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

from typing import List

from setuptools import setup
from setuptools.command.test import test


class PytestTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = [
            'tests/',
        ]
        self.test_suite = True

    def run_tests(self):
        from sys import exit
        from pytest import main
        exit(main(self.test_args))


def parse_requires(file: str) -> List[str]:
    deps = []
    with open(f'extra/{file}') as req_file:
        entries = [s.split('#')[0].strip() for s in req_file.readlines()]
    for dep in entries:
        if not dep or dep.startswith('#'):
            continue
        elif dep.startswith('-r '):
            deps.extend(parse_requires(dep.split()[1]))
            continue
        deps.append(dep)
    return deps


# Note: We can't use setuptool’s requirements support as it only a list value,
# and doesn’t support pip’s inclusion mechanism
install_requires = parse_requires('requirements.txt')
tests_require = parse_requires('requirements-test.txt')

if __name__ == '__main__':
    setup(
        install_requires=install_requires,
        tests_require=tests_require,
        cmdclass={'test': PytestTest},
    )
