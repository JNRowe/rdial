Usage
=====

The :program:`rdial` script is the main workhorse of :mod:`rdial`.

See :doc:`getting_started` for basic usage examples.

Options
-------

.. program:: rdial

.. option:: --version

   Show the version and exit.

.. option:: -d <directory>, --directory=<directory>

   Database location, defaults to ``${XDG_DATA_HOME:-~/.local/share}/rdial``.

.. option:: --backup/--no-backup

   Write data file backups.

.. option:: --config <file>

   File to read configuration data from, defaults to
   ``${XDG_CONFIG_HOME:-~/.config}/rdial/config``.

.. option:: --help

   Show help message and exit.

Commands
--------

``fsck`` - Check storage consistency
''''''''''''''''''''''''''''''''''''

.. program:: rdial fsck

::

    rdial fsck [--help]

.. option:: --help

   Show help message and exit.

``start`` - Start task
''''''''''''''''''''''

.. program:: rdial start

::

    rdial start [--help] [-x] [-n] [-t time] <task>

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: -n, --new

   Start a new task.

.. option:: -t <time>, --time <time>

   Manually set start time for task.

.. option:: --help

   Show help message and exit.

``stop`` - Stop task
''''''''''''''''''''

.. program:: rdial stop

::

    rdial stop [--help] [-m <message>] [--amend]

.. option:: -m <message>, --message=<message>

   Closing message.

.. option:: -F <file>, --file <file>

   Read closing message from file.

.. option:: --amend

   Amend previous stop entry.

.. option:: --help

   Show help message and exit.

``switch`` - Switch to another task
'''''''''''''''''''''''''''''''''''

.. program:: rdial switch

::

    rdial switch [--help] [-x] [-n] [-m <message>] [task]

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: -n, --new

   Start a new task.

.. option:: -m <message>, --message <message>

   Closing message for current task.

.. option:: -F <file>, --file <file>

   Read closing message for current task from file.

.. option:: --help

   Show help message and exit.

.. _run-subcommand-label:

``run`` - Run command with timer
''''''''''''''''''''''''''''''''

.. program:: rdial run

::

    rdial run [--help] [-x] [-n] [-t time] [-m message] [-F file] [-c command] <task>

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: -n, --new

   Start a new task.

.. option:: -t <time>, --time <time>

   Manually set start time for task.

.. option:: -m <message>, --message <message>

   Closing message for current task.

.. option:: -F <file>, --file <file>

   Read closing message for current task from file.

.. option:: -c <command>, --command <command>

   Command to run.

.. option:: --help

   Show help message and exit.

``wrapper`` - Run predefined command with timer
'''''''''''''''''''''''''''''''''''''''''''''''

.. program:: rdial wrapper

::

    rdial wrapper [--help] [-t time] [-m message] [-F file] <wrapper>

See :ref:`run wrappers configuration <run-wrappers-label>`.

.. option:: -t <time>, --time <time>

   Manually set start time for task.

.. option:: -m <message>, --message <message>

   Closing message for current task.

.. option:: -F <file>, --file <file>

   Read closing message for current task from file.

.. option:: --help

   Show help message and exit.

``report`` - Report time tracking data
''''''''''''''''''''''''''''''''''''''

.. program:: rdial report

::

    rdial report [--help] [-d <duration>] [-s <order] [-r] [--html] [--human] <task>

.. option:: -d <duration>, --duration=<duration>

   Filter events for specified time period {day,week,month,year,all}.

.. option:: -s <order>, --sort=<order>

   Field to sort by {task,time}.

.. option:: -r, --reverse

   Reverse sort order.

.. option:: --html

   Produce HTML output.

.. option:: --human

   Produce human-readable output.

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: --help

   Show help message and exit.

``running`` - Display running task, if any
''''''''''''''''''''''''''''''''''''''''''

.. program:: rdial running

::

    rdial running [--help]

.. option:: --help

   Show help message and exit.

``last`` - Display last task, if any
''''''''''''''''''''''''''''''''''''

.. program:: rdial last

::

    rdial last [--help]

.. option:: --help

   Show help message and exit.

``ledger`` - Generate ``ledger`` compatible data file
'''''''''''''''''''''''''''''''''''''''''''''''''''''

.. program:: rdial ledger

::

    rdial ledger [--help] [-d <duration>] [-r RATE] [task]

.. option:: -d <duration>, --duration=<duration>

   Filter events for specified time period {day,week,month,year,all}.

.. option:: -r <rate>, --rate <rate>

   Hourly rate for task output.

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: --help

   Show help message and exit.
