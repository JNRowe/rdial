#! /usr/bin/python -tt
# coding=utf-8
"""setup.py - Setuptools tasks and config for rdial"""
# Copyright © 2011, 2012, 2013  James Rowe <jnrowe@gmail.com>
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
    url="https://github.com/JNRowe/rdial/",
    author="James Rowe",
    author_email="jnrowe@gmail.com",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
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
    packages=['rdial', ],
    include_package_data=False,
    entry_points={'console_scripts': ['rdial = rdial.cmdline:main', ]},
    zip_safe=False,
    install_requires=install_requires,
)
