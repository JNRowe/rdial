#! /usr/bin/python -tt

import imp

from setuptools import setup

# Hack to import _version file without importing rdial/__init__.py, its
# purpose is to allow import without requiring dependencies at this point.
ver_file = open("rdial/_version.py")
_version = imp.load_module("_version", ver_file, ver_file.name,
                           (".py", ver_file.mode, imp.PY_SOURCE))

setup(
    name='rdial',
    version=_version.dotted,
    url="https://github.com/JNRowe/rdial/",
    author="James Rowe",
    author_email="jnrowe@gmail.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
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
        'Topic :: Office/Business',
        'Topic :: Office/Business :: News/Diary',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Text Processing :: Filters',
        'Topic :: Utilities',
    ],
    packages=['rdial', ],
    include_package_data=False,
    entry_points={'console_scripts': ['rdial = rdial:main', ]},
    zip_safe=False,
    install_requires=['argh', 'isodate', 'prettytable'],
)
