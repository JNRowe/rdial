Usage
=====

The :program:`rdial` script is the main workhorse of :mod:`rdial`.

See :doc:`getting_started` for basic usage examples.

Options
-------

.. program:: rdial

.. cmdoption:: --version

   show program's version number and exit

.. cmdoption:: -h, --help

   show program's help message and exit

.. cmdoption:: -d <directory>, --directory=<directory>

   database location, defaults to ``${XDG_DATA_HOME:-/.local}/rdial``

Commands
--------

``start`` - Start task
''''''''''''''''''''''

.. program:: rdial start

::

    rdial.py start [-h] [-t time] <task>

.. cmdoption:: -n, --new

   start a new task

.. cmdoption:: -t <time>, --time <time>

   manually set start time for task

.. cmdoption:: -x, --from-dir

   use directory name as task

``stop`` - Stop task
''''''''''''''''''''

.. program:: rdial stop

::

    rdial stop [-h] [-m <message>] [--amend]

.. cmdoption:: -m <message>, --message=<message>

   closing message

.. cmdoption:: --amend

   amend previous stop entry

``report`` - Report time tracking data
''''''''''''''''''''''''''''''''''''''

.. program:: rdial report

::

    rdial report [-h] [-d <duration>] [-s <order] [-r] [--html] [--human] <task>

.. cmdoption:: -d <duration>, --duration=<duration>

   filter events for specified time period {day,week,month,year,all}

.. cmdoption:: -s <order>, --sort=<order>

   field to sort by {task,time}

.. cmdoption:: -r, --reverse

   reverse sort order

.. cmdoption:: --html

   produce HTML output

.. cmdoption:: --human

   produce human-readable output

.. cmdoption:: -x, --from-dir

   use directory name as task

``running`` - Display running task, if any
''''''''''''''''''''''''''''''''''''''''''

.. program:: rdial running

::

    rdial running [-h]

``last`` - Display last task, if any
''''''''''''''''''''''''''''''''''''

.. program:: rdial last

::

    rdial last [-h]

``ledger`` - Generate ``ledger`` compatible data file
'''''''''''''''''''''''''''''''''''''''''''''''''''''

.. program:: rdial ledger

::

    rdial ledger [-h] [-d <duration>] [-r RATE] [task]

.. cmdoption:: -d <duration>, --duration=<duration>

   filter events for specified time period {day,week,month,year,all}

.. cmdoption:: -r <rate>, --rate <rate>

   hourly rate for task output

.. cmdoption:: -x, --from-dir

   use directory name as task
