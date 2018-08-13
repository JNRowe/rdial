Usage
=====

The :program:`rdial` script is the main workhorse of :mod:`rdial`.

See the :doc:`getting started <getting_started>` for basic usage examples.

Options
-------

.. program:: rdial

.. option:: --version

   Show the version and exit.

.. option:: -d <directory>, --directory=<directory>

   Database location, defaults to ``${XDG_DATA_HOME:-~/.local/share}/rdial``.

.. option:: --backup/--no-backup

   Write data file backups.

.. option:: --cache/--no-cache

   Do not write cache files.

.. option:: --config <file>

   File to read configuration data from, defaults to
   ``${XDG_CONFIG_HOME:-~/.config}/rdial/config``.

.. option:: -i, --interactive/--no-interactive

   Support interactive message editing.

.. option:: --colour/--no-colour

   Output colourised informational text.

.. option:: --help

   Show help message and exit.

Commands
--------

``fsck`` - Check storage consistency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial fsck

::

    rdial fsck [--help]

.. option:: --help

   Show help message and exit.

``start`` - Start task
~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial start

::

    rdial start [--help] [-x] [-n] [-t time] <task>

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: -c, --continue

   Restart previous task.

.. option:: -n, --new

   Start a new task.

.. option:: -t <time>, --time <time>

   Manually set start time for task.

.. option:: --help

   Show help message and exit.

``stop`` - Stop task
~~~~~~~~~~~~~~~~~~~~

.. program:: rdial stop

::

    rdial stop [--help] [-F file] [-m message] [--amend]

.. option:: -F <file>, --file <file>

   Read closing message from file.

.. option:: -m <message>, --message=<message>

   Closing message.

.. option:: --amend

   Amend previous stop entry.

.. option:: --help

   Show help message and exit.

``switch`` - Switch to another task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial switch

::

    rdial switch [--help] [-x] [-n] [-F file] [-m message] [task]

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: -n, --new

   Start a new task.

.. option:: -t <time>, --time <time>

   Manually set start time for task.

.. option:: -F <file>, --file <file>

   Read closing message for current task from file.

.. option:: -m <message>, --message <message>

   Closing message for current task.

.. option:: --help

   Show help message and exit.

.. _run-subcommand-label:

``run`` - Run command with timer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial run

::

    rdial run [--help] [-x] [-n] [-t time] [-F file] [-m message] [-c command] <task>

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: -n, --new

   Start a new task.

.. option:: -t <time>, --time <time>

   Manually set start time for task.

.. option:: -F <file>, --file <file>

   Read closing message for current task from file.

.. option:: -m <message>, --message <message>

   Closing message for current task.

.. option:: -c <command>, --command <command>

   Command to run.

.. option:: --help

   Show help message and exit.

``wrapper`` - Run predefined command with timer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial wrapper

::

    rdial wrapper [--help] [-t time] [-F file] [-m message] <wrapper>

See :ref:`run wrappers configuration <run-wrappers-label>`.

.. option:: -t <time>, --time <time>

   Manually set start time for task.

.. option:: -F <file>, --file <file>

   Read closing message for current task from file.

.. option:: -m <message>, --message <message>

   Closing message for current task.

.. option:: --help

   Show help message and exit.

``report`` - Report time tracking data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial report

::

    rdial report [--help] [-x] [--stats] [-d <duration>] [-s <order] [-r] [--style <style>] <task>

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: --stats

    Display database statistics.

.. option:: -d <duration>, --duration=<duration>

   Filter events for specified time period {day,week,month,year,all}.

.. option:: -s <order>, --sort=<order>

   Field to sort by {task,time}.

.. option:: -r, --reverse/--no-reverse

   Reverse sort order.

.. option:: --style

   Table output style {fancy_grid,grid,html,latex,latex_booktabs,mediawiki,orgtbl,pipe,plain,psql,rst,simple,tsv}

   See the tabulate_ documentation for descriptions of the supported formats
   for your installation.

.. _tabulate: https://pypi.org/project/tabulate/

.. option:: --help

   Show help message and exit.

``running`` - Display running task, if any
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial running

::

    rdial running [--help]

.. option:: --help

   Show help message and exit.

``last`` - Display last task, if any
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial last

::

    rdial last [--help]

.. option:: --help

   Show help message and exit.

``ledger`` - Generate ``ledger`` compatible data file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: rdial ledger

::

    rdial ledger [--help] [-x] [-d <duration>] [-r RATE] [task]

.. option:: -x, --from-dir

   Use directory name as task name.

.. option:: -d <duration>, --duration=<duration>

   Filter events for specified time period {day,week,month,year,all}.

.. option:: -r <rate>, --rate <rate>

   Hourly rate for task output.

.. option:: --help

   Show help message and exit.
