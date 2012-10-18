#! /usr/bin/python -tt

from setuptools import setup

from rdial import _version

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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
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
    install_requires=['isodate', 'prettytable'],
)
