#! /usr/bin/env python
# coding=utf-8
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

import imp
import sys

from setuptools import setup

# Hack to import _version file without importing rdial/__init__.py, its
# purpose is to allow import without requiring dependencies at this point.
with open('rdial/_version.py') as ver_file:
    _version = imp.load_module('_version', ver_file, ver_file.name,
                               ('.py', ver_file.mode, imp.PY_SOURCE))


def parse_requires(file):
    deps = []
    with open('extra/%s' % file) as req_file:
        entries = map(lambda s: s.split('#')[0].strip(), req_file.readlines())
    for dep in entries:
        if not dep or dep.startswith('#'):
            continue
        elif dep.startswith('-r '):
            deps.extend(parse_requires(dep.split()[1]))
            continue
        elif ';' in dep:
            dep, marker = dep.split(';')
            if not eval(marker.strip(),
                        {'python_version': '%s.%s' % sys.version_info[:2]}):
                continue
        deps.append(dep)
    return deps


install_requires = parse_requires('requirements.txt')

tests_require = parse_requires('requirements-test.txt')

with open('README.rst') as f:
    long_description = f.read()

if __name__ == '__main__':
    setup(
        name='rdial',
        version=_version.dotted,
        description='Simple time tracking for simple people',
        long_description=long_description,
        author='James Rowe',
        author_email='jnrowe@gmail.com',
        url='https://github.com/JNRowe/rdial',
        license='GPL-3',
        keywords='timetracking task report',
        packages=['rdial', ],
        include_package_data=True,
        package_data={'': ['config', 'rdial/locale/*/LC_MESSAGES/*.mo']},
        entry_points={'console_scripts': ['rdial = rdial.cmdline:main', ]},
        install_requires=install_requires,
        tests_require=tests_require,
        zip_safe=False,
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Other Audience',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Office/Business',
            'Topic :: Office/Business :: News/Diary',
            'Topic :: Office/Business :: Scheduling',
            'Topic :: Other/Nonlisted Topic',
            'Topic :: Utilities',
        ],
    )
