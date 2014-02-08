Usage
=====

The :program:`rdial` script is the main workhorse of :mod:`rdial`.

See :doc:`getting_started` for basic usage examples.

Options
-------

.. program:: rdial

.. option:: --version

   show program's version number and exit

.. option:: -h, --help

   show program's help message and exit

.. option:: -d <directory>, --directory=<directory>

   database location, defaults to ``${XDG_DATA_HOME:-/.local}/rdial``

.. option:: --no-backup

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

.. option:: -x, --from-dir

   use directory name as task

.. option:: -n, --new

   start a new task

.. option:: -t <time>, --time <time>

   manually set start time for task

``stop`` - Stop task
''''''''''''''''''''

.. program:: rdial stop

::

    rdial stop [-h] [-m <message>] [--amend]

.. option:: -m <message>, --message=<message>

   closing message

.. option:: -F <file>, --file <file>

   read closing message from file

.. option:: --amend

   amend previous stop entry

``switch`` - Switch to another task
'''''''''''''''''''''''''''''''''''

.. program:: rdial switch

::

    rdial switch [-h] [-x] [-n] [-m <message>] [task]

.. option:: -x, --from-dir

   use directory name as task

.. option:: -n, --new

   start a new task

.. option:: -m <message>, --message <message>

   closing message for current task

.. option:: -F <file>, --file <file>

   read closing message for current task from file

.. _run-subcommand-label:

``run`` - Run command with timer
''''''''''''''''''''''''''''''''

.. program:: rdial run

::

    rdial run [-h] [-x] [-n] [-t time] [-m message] [-F file] [-c command] <task>

.. option:: -x, --from-dir

   use directory name as task

.. option:: -n, --new

   start a new task

.. option:: -t <time>, --time <time>

   manually set start time for task

.. option:: -m <message>, --message <message>

   closing message for current task

.. option:: -F <file>, --file <file>

   read closing message for current task from file

.. option:: -c <command>, --command <command>

   command to run

``wrapper`` - Run predefined command with timer
'''''''''''''''''''''''''''''''''''''''''''''''

.. program:: rdial wrapper

::

    rdial wrapper [-h] [-t time] [-m message] [-F file] <wrapper>

See :ref:`run wrappers configuration <run-wrappers-label>`.

.. option:: -t <time>, --time <time>

   manually set start time for task

.. option:: -m <message>, --message <message>

   closing message for current task

.. option:: -F <file>, --file <file>

   read closing message for current task from file

``report`` - Report time tracking data
''''''''''''''''''''''''''''''''''''''

.. program:: rdial report

::

    rdial report [-h] [-d <duration>] [-s <order] [-r] [--html] [--human] <task>

.. option:: -d <duration>, --duration=<duration>

   filter events for specified time period {day,week,month,year,all}

.. option:: -s <order>, --sort=<order>

   field to sort by {task,time}

.. option:: -r, --reverse

   reverse sort order

.. option:: --html

   produce HTML output

.. option:: --human

   produce human-readable output

.. option:: -x, --from-dir

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

.. option:: -d <duration>, --duration=<duration>

   filter events for specified time period {day,week,month,year,all}

.. option:: -r <rate>, --rate <rate>

   hourly rate for task output

.. option:: -x, --from-dir

   use directory name as task
