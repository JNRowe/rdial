rdial - Simple time tracking for simple people
==============================================

.. warning::
   This tool is incomplete.  It was written, in part, for use as a toy project
   in a talk on testing methodologies and hasn't been worked on since!

``rdial`` is a simple way to track the time you spend on tasks.  It tracks the
name of a task, its start time and its duration… nothing more.

``rdial`` is released under the `GPL v3`_ license.

Requirements
------------

``rdial``'s dependencies outside of the standard library are:

* argh_
* isodate_
* prettytable_

It should work with any version of Python_ 2.5 or newer.  If ``rdial`` doesn't
work with the version of Python you have installed, file an issue_ and I'll
endeavour to fix it.

The module has been tested on many UNIX-like systems, including Linux and OS X,
but it should work fine on other systems too.

To run the tests you'll need nose_ and nose-lettuce_.  Once you have both
packages you can run the tests with one of the following commands::

    $ ./setup.py nosetests
    $ nosetests --with-lettuce --with-coverage --cover-package=rdial -s

Database
--------

The database is just a simple text file, making it very easy to use and abuse in
other applications.  A sample database would be::

    task,2011-05-04T08:00:00Z,PT01H00M00S
    task2,2011-05-04T09:15:00Z,PT00H15M00S
    task,2011-05-04T09:30:00Z,

The format is a CSV file containing the following fields:

#. Task name
#. Start time expressed in UTC
#. Task duration

The start time and duration fields are given as ISO-8601 formatted strings.

If a line does not contain a duration entry then the task is considered to be
currently running.

Interface
---------

::

    $ rdial.py start <task_name>
    $ rdial.py stop
    $ rdial.py report
    +-------+-------------+
    | task  |     time    |
    +-------+-------------+
    | task  | PT01H00M00S |
    | task2 | PT00H15M00S |
    +-------+-------------+

Hacking
-------

Patches are most welcome, but I'd appreciate it if you could follow the
guidelines below to make it easier to integrate your changes.  These are
guidelines however, and as such can be broken if the need arises or you
just want to convince me that your style is better.

* `PEP 8`_, the style guide, should be followed where possible.
* While support for Python versions prior to v2.5 may be added in the future if
  such a need were to arise, you are encouraged to use v2.5 features now.
* All new classes and methods should be accompanied by new tests, and Sphinx_
  ``autodoc``-compatible descriptions.

Bugs
----

If you find any problems, bugs or just have a question about this package either
file an issue_ or drop me a mail_.

If you've found a bug please attempt to include a minimal testcase so I can
reproduce the problem, or even better a patch!

.. _GPL v3: http://www.gnu.org/licenses/
.. _argh: http://pypi.python.org/pypi/argh/
.. _isodate: http://pypi.python.org/pypi/isodate/
.. _prettytable: http://code.google.com/p/prettytable/
.. _Python: http://www.python.org/
.. _issue: https://github.com/JNRowe/rdial/issues
.. _nose: http://pypi.python.org/pypi/nose
.. _nose-lettuce: http://github.com/passy/nose-lettuce
.. _PEP 8: http://www.python.org/dev/peps/pep-0008/
.. _Sphinx: http://sphinx.pocoo.org/
.. _mail: jnrowe@gmail.com
