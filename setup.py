#! /usr/bin/env python3
"""setup.py - Setuptools tasks and config for rdial"""
# Copyright © 2011-2017  James Rowe <jnrowe@gmail.com>
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

from configparser import ConfigParser
from importlib.util import module_from_spec, spec_from_file_location

from setuptools import setup
from setuptools.command.test import test


class PytestTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = ['tests/', ]
        self.test_suite = True

    def run_tests(self):
        from sys import exit
        from pytest import main
        exit(main(self.test_args))


def import_file(package, fname):
    """Import file directly.

    This is a hack to import files from packages without importing
    <package>/__init__.py, its purpose is to allow import without requiring
    all the dependencies at this point.

    Args:
        package (str): Package to import from
        fname (str): File to import
    Returns:
        types.ModuleType: Imported module
    """
    mod_name = fname.rstrip('.py')
    spec = spec_from_file_location(mod_name, '{}/{}'.format(package, fname))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_list(s):
    return s.strip().splitlines()


def parse_requires(file):
    deps = []
    with open('extra/{}'.format(file)) as req_file:
        entries = [s.split('#')[0].strip() for s in req_file.readlines()]
    for dep in entries:
        if not dep or dep.startswith('#'):
            continue
        elif dep.startswith('-r '):
            deps.extend(parse_requires(dep.split()[1]))
            continue
        deps.append(dep)
    return deps


conf = ConfigParser()
conf.read('setup.cfg')
metadata = dict(conf['metadata'])

install_requires = parse_requires('requirements.txt')

tests_require = parse_requires('requirements-test.txt')

metadata = dict(conf['metadata'])
for k in ['classifiers', 'packages', 'py_modules']:
    if k in metadata:
        metadata[k] = make_list(metadata[k])

for k in ['include_package_data', ]:
    if k in metadata:
        metadata[k] = conf.getboolean('metadata', k)

for k in ['entry_points', 'package_data']:
    if k in metadata:
        metadata[k] = eval(metadata[k], {'__builtins__': {}})

with open('README.rst') as readme:
    metadata['long_description'] = readme.read()

_version = import_file(metadata['name'], '_version.py')

if __name__ == '__main__':
    setup(
        version=_version.dotted,
        install_requires=install_requires,
        tests_require=tests_require,
        cmdclass={'test': PytestTest},
        zip_safe=False,
        **metadata,
    )
