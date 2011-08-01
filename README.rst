rdial - Simple time tracking for simple people
==============================================

.. warning::
   This tool is incomplete.  It was written, in part, for use in a talk on testing
   methodologies and hasn't been worked on since!

``rdial`` is a simple way to track the time you spend on tasks.

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

If a line does not contain a duration entry then the task is currently running.

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

.. _GPL v3: http://www.gnu.org/licenses/
.. _argh: http://pypi.python.org/pypi/argh/
.. _isodate: http://pypi.python.org/pypi/isodate/
.. _prettytable: http://code.google.com/p/prettytable/
.. _Python: http://www.python.org/
.. _issue: https://github.com/JNRowe/rdial/issues
