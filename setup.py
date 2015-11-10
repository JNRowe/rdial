#! /usr/bin/env python
# coding=utf-8
"""setup.py - Setuptools tasks and config for rdial"""
# Copyright © 2011-2015  James Rowe <jnrowe@gmail.com>
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

import imp

from sys import version_info
from warnings import warn

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
        dep = dep
        if dep.startswith('-r '):
            deps.extend(parse_requires(dep.split()[1]))
        else:
            deps.append(dep)
    return deps

try:
    install_requires = parse_requires('requirements-py%s%s.txt'
                                      % version_info[:2])
except IOError:
    warn('Unsupported Python version please open an issue!', RuntimeWarning)
    install_requires = parse_requires('requirements-base.txt')

test_requires = parse_requires('requirements-test.txt')

with open('README.rst') as f:
    long_description = f.read()

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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: News/Diary',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Utilities',
    ],
)
