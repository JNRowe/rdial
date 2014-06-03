rdial - Simple time tracking for simple people
==============================================

.. image:: https://secure.travis-ci.org/JNRowe/rdial.png?branch=master
   :target: http://travis-ci.org/JNRowe/rdial
   :alt: Test state on master

.. image:: https://pypip.in/v/rdial/badge.png
   :target: https://crate.io/packages/rdial/
   :alt: Current PyPI release

.. image:: https://pypip.in/d/rdial/badge.png
   :target: https://crate.io/packages/rdial/
   :alt: Number of downloads from PyPI

``rdial`` is a simple way to track the time you spend on tasks.  It tracks the
name of a task, its start time and its duration… nothing more.

``rdial`` is released under the `GPL v3`_ license.

Requirements
------------

``rdial``'s dependencies outside of the standard library are:

* arrow_
* blessings_
* click_
* configobj_
* prettytable_

It should work with any version of Python_ 2.6 or newer.  If ``rdial`` doesn't
work with the version of Python you have installed, file an issue_ and I'll
endeavour to fix it.

The module has been tested on many UNIX-like systems, including Linux and OS X,
but it should work fine on other systems too.

To run the tests you'll need nose2_.  Once you have nose2_ installed you can run
the tests with the following commands:

.. code-block:: console

    $ nose2 -v tests

Database
--------

The database is just a directory of simple text files, making it very easy to
use and abuse in other applications.  A sample database could be a file named
``task.csv`` with the following contents::

    start,delta,message
    2011-05-04T08:00:00Z,PT01H00M00S,working on issue 4
    2011-05-04T09:30:00Z,,

and a ``task2.csv`` file with the following contents::

    start,delta,message
    2011-05-04T09:15:00Z,PT00H15M00S

The format is a CSV file containing the following fields:

1. Start time expressed in UTC
2. Task duration
3. Message associated with the event

The start time and duration fields are given as ISO-8601 formatted strings.

If a line does not contain a duration entry then the task is considered to be
currently running.

Interface
---------

.. code-block:: console

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

I'd like to thank the following people who have contributed to ``rdial``.

Patches
'''''''

* Nathan McGregor

Bug reports
'''''''''''

* James Gaffney

Ideas
'''''

* Adam Baxter
* Kevin Simmons

If I've forgotten to include your name I wholeheartedly apologise.  Just drop me
a mail_ and I'll update the list!

Bugs
----

If you find any problems, bugs or just have a question about this package either
file an issue_ or drop me a mail_.

If you've found a bug please attempt to include a minimal testcase so I can
reproduce the problem, or even better a patch!

.. _GPL v3: http://www.gnu.org/licenses/
.. _arrow: https://crate.io/packages/arrow/
.. _blessings: https://crate.io/packages/blessings/
.. _click: https://crate.io/packages/click/
.. _configobj: https://crate.io/packages/configobj/
.. _prettytable: http://code.google.com/p/prettytable/
.. _Python: http://www.python.org/
.. _issue: https://github.com/JNRowe/rdial/issues
.. _nose2: https://crate.io/packages/nose2/
.. _mail: jnrowe@gmail.com
