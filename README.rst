rdial - Simple time tracking for simple people
==============================================

.. image:: https://img.shields.io/travis/JNRowe/rdial.png
   :target: https://travis-ci.org/JNRowe/rdial
   :alt: Test state on master

.. image:: https://img.shields.io/coveralls/JNRowe/rdial/master.png
   :target: https://coveralls.io/repos/JNRowe/rdial
   :alt: Coverage state on master

.. image:: https://img.shields.io/pypi/v/rdial.png
   :target: https://pypi.python.org/pypi/rdial/
   :alt: Current PyPI release

``rdial`` is a simple way to track the time you spend on tasks.  It tracks the
name of a task, its start time, its duration and optionally a message… nothing
more.

``rdial`` is released under the `GPL v3`_ license.

Requirements
------------

``rdial``’s mandatory dependencies outside of the standard library are:

* ciso8601_ ≥ 1.0.1
* click_ ≥ 5.1
* jnrbase_ ``[colour]`` ≥ 0.5.0
* tabulate_

It should work with Python_ version 3.5, or newer.  If ``rdial`` doesn’t work
with the version of Python you have installed, file an issue_ and I’ll
endeavour to fix it.

The package has been tested on many UNIX-like systems, including Linux and OS
X, but it may work fine on other systems too.

To run the tests you’ll need pytest_.  Once you have pytest_ installed you can
run the tests with the following commands:

.. code:: console

    $ pytest tests

Database
--------

The database is just a directory of simple text files, making it useful to use
and abuse in other applications.  A sample database could be a file named
``task.csv`` with the following contents:

.. code:: text

    start,delta,message
    2011-05-04T08:00:00Z,PT01H00M00S,working on issue 4
    2011-05-04T09:30:00Z,,

and a ``task2.csv`` file with the following contents:

.. code:: text

    start,delta,message
    2011-05-04T09:15:00Z,PT00H15M00S,

The format is a CSV file containing the following fields:

1. Start time expressed in UTC
2. Task duration
3. Message associated with the event

The start time and duration fields are given as `ISO 8601`_ formatted strings.

If a line does not contain a duration entry, then the task is considered to be
running.

Interface
---------

.. code:: console

    $ rdial start <task_name>
    $ rdial stop
    $ rdial report
    +-------+----------------+
    | task  | time           |
    +-------+----------------+
    | task  |        1:00:00 |
    | task2 | 1 day, 0:15:00 |
    +-------+----------------+

Contributors
------------

I’d like to thank the following people who have contributed to ``rdial``.

Patches
'''''''

* Nathan McGregor

Bug reports
'''''''''''

* Delphine Beauchemin
* Henry Richards
* James Gaffney
* Ryan Sutton
* Stephen Thorne

Ideas
'''''

* Adam Baxter
* Kevin Simmons

If I’ve forgotten to include your name I wholeheartedly apologise.  Just drop me
a mail_ and I’ll update the list!

Bugs
----

If you find any problems, bugs or just have a question about this package either
file an issue_ or drop me a mail_.

If you’ve found a bug please try to include a minimal testcase that reproduces
the problem, or even better a patch that fixes it!

.. _GPL v3: http://www.gnu.org/licenses/
.. _ciso8601: https://pypi.python.org/pypi/ciso8601/
.. _click: https://pypi.python.org/pypi/click/
.. _jnrbase: https://pypi.python.org/pypi/jnrbase/
.. _tabulate: https://pypi.python.org/pypi/tabulate/
.. _Python: http://www.python.org/
.. _issue: https://github.com/JNRowe/rdial/issues
.. _pytest: https://pypi.python.org/packages/pytest/
.. _ISO 8601:  https://en.wikipedia.org/wiki/Iso8601
.. _mail: jnrowe@gmail.com
