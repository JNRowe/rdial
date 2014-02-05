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

.. cmdoption:: --no-backup

   do not write data file backups

Commands
--------

``fsck`` - Check storage consistency
''''''''''''''''''''''''''''''''''''

.. program:: rdial fsck

::

    rdial fsck [-h]

``start`` - Start task
''''''''''''''''''''''

.. program:: rdial start

::

    rdial start [-h] [-x] [-n] [-t time] <task>

.. cmdoption:: -x, --from-dir

   use directory name as task

.. cmdoption:: -n, --new

   start a new task

.. cmdoption:: -t <time>, --time <time>

   manually set start time for task

``stop`` - Stop task
''''''''''''''''''''

.. program:: rdial stop

::

    rdial stop [-h] [-m <message>] [--amend]

.. cmdoption:: -m <message>, --message=<message>

   closing message

.. cmdoption:: -F <file>, --file <file>

   read closing message from file

.. cmdoption:: --amend

   amend previous stop entry

``switch`` - Switch to another task
'''''''''''''''''''''''''''''''''''

.. program:: rdial switch

::

    rdial switch [-h] [-x] [-n] [-m <message>] [task]

.. cmdoption:: -x, --from-dir

   use directory name as task

.. cmdoption:: -n, --new

   start a new task

.. cmdoption:: -m <message>, --message <message>

   closing message for current task

.. cmdoption:: -F <file>, --file <file>

   read closing message for current task from file

.. _run-subcommand-label:

``run`` - Run command with timer
''''''''''''''''''''''''''''''''

.. program:: rdial run

::

    rdial run [-h] [-x] [-n] [-t time] [-m message] [-F file] [-c command] <task>

.. cmdoption:: -x, --from-dir

   use directory name as task

.. cmdoption:: -n, --new

   start a new task

.. cmdoption:: -t <time>, --time <time>

   manually set start time for task

.. cmdoption:: -m <message>, --message <message>

   closing message for current task

.. cmdoption:: -F <file>, --file <file>

   read closing message for current task from file

.. cmdoption:: -c <command>, --command <command>

   command to run

``wrapper`` - Run predefined command with timer
'''''''''''''''''''''''''''''''''''''''''''''''

.. program:: rdial wrapper

::

    rdial wrapper [-h] [-t time] [-m message] [-F file] <wrapper>

See :ref:`run wrappers configuration <run-wrappers-label>`.

.. cmdoption:: -t <time>, --time <time>

   manually set start time for task

.. cmdoption:: -m <message>, --message <message>

   closing message for current task

.. cmdoption:: -F <file>, --file <file>

   read closing message for current task from file

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
