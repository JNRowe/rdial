#! /usr/bin/env python
# coding=utf-8
"""setup.py - Setuptools tasks and config for rdial"""
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

from setuptools import setup

from rdial import _version

install_requires = map(str.strip, open('extra/requirements.txt').readlines())

setup(
    name='rdial',
    version=_version.dotted,
    description='Simple time tracking for simple people',
    long_description=open('README.rst').read(),
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
        'Topic :: Office/Business',
        'Topic :: Office/Business :: News/Diary',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Text Processing :: Filters',
        'Topic :: Utilities',
    ],
)
