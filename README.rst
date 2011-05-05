rdial - Simple time tracking for simple people
==============================================

``rdial`` is a simple way to track the time you spend on tasks.

``rdial`` is released under the `GPL v3`_ license.

Requirements
------------

``rdial`` does not depend on any modules that aren't included in Python_'s
standard library, and as such should run with Python 2.6 or newer [#]_.  If
``rdial`` doesn't work with the version of Python you have installed, file an
issue_ and I'll endeavour to fix it.

The module has been tested on many UNIX-like systems, including Linux and OS X,
but it should work fine on other systems too.

.. [#] If you still use Python v2.5 only small changes are required, for
       example using the pre-``namedtuple`` syntax for the
       ``inspect.getargspec`` calls

Database
--------

The database is just a simple text file, making it very easy to use and abuse in
other applications.  A sample database would be::

    project,2011-05-04T08:00:00Z,PT01H00M00S
    project2,2011-05-04T09:15:00Z,PT00H15M00S
    project,2011-05-04T09:30:00Z,

The format is a CSV file containing the following fields:

#. Project name
#. Start time expressed in UTC
#. Task duration

The start time and duration fields are given as ISO-8601 formatted strings.

If a line does not contain a duration entry then the task is currently running.

Interface
---------

::

    $ rdial.py start <project_name>
    $ rdial.py stop
    $ rdial.py [summary]
    project  PT01H00M00S
    project2 PT00H15M00S

.. _GPL v3: http://www.gnu.org/licenses/
.. _Python: http://www.python.org/
.. _issue: https://github.com/JNRowe/rdial/issues
