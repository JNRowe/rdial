:Author: James Rowe <jnrowe@gmail.com>
:Date: 2012-06-30
:Copyright: GPL v3
:Manual section: 1
:Manual group: user

rdial
=====

Simple time tracking for simple people
--------------------------------------

SYNOPSIS
--------

    rdial [option]... <command>

DESCRIPTION
-----------

:mod:`rdial` is a simple way to track the time you spend on tasks.  It tracks
the name of a task, its start time and its duration… nothing more.

OPTIONS
-------

.. program:: rdial

.. option:: --version

    Show the version and exit.

.. option:: -d <directory>, --directory=<directory>

    Database location, defaults to ``${XDG_DATA_HOME:-~/.local/share}/rdial``.

.. option:: --backup, --no-backup

    Write data file backups.

.. option:: --cache, --no-cache

    Do not write cache files.

.. option:: --config <file>

    File to read configuration data from, defaults to
    ``${XDG_CONFIG_HOME:-~/.config}/rdial/config``.

.. option:: -i, --interactive, --no-interactive

    Support interactive message editing.

.. option:: --colour, --no-colour

    Output colourised informational text.

.. option:: --help

    Show help message and exit.

COMMANDS
--------

``fsck``
''''''''

.. program:: rdial fsck

Check storage consistency

.. option:: --help

    Show help message and exit.

``start``
'''''''''

.. program:: rdial start

Start task

.. option:: -x, --from-dir

    Use directory name as task name.

.. option:: -n, --new

    Start a new task.

.. option:: -t <time>, --time <time>

    Manually set start time for task.

.. option:: --help

    Show help message and exit.

``stop``
''''''''

.. program:: rdial stop

Stop task

.. option:: -F <file>, --file <file>

    Read closing message from file.

.. option:: -m <message>, --message=<message>

    Closing message.

.. option:: --amend

    Amend previous stop entry.

.. option:: --help

    Show help message and exit.

``switch``
''''''''''

.. program:: rdial switch

Switch to another task

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

``run``
'''''''

.. program:: rdial run

Run command with timer

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

``wrapper``
'''''''''''

.. program:: rdial wrapper

Run predefined command with timer

.. option:: -t <time>, --time <time>

    Manually set start time for task.

.. option:: -F <file>, --file <file>

    Read closing message for current task from file.

.. option:: -m <message>, --message <message>

    Closing message for current task.

.. option:: --help

    Show help message and exit.

``report``
''''''''''

.. program:: rdial report

Report time tracking data

.. option:: -x, --from-dir

    Use directory name as task name.

.. option:: --stats

    Display database statistics.

.. option:: -d <duration>, --duration=<duration>

    Filter events for specified time period {day,week,month,year,all}.

.. option:: -s <order>, --sort=<order>

    Field to sort by {task,time}.

.. option:: -r, --reverse, --no-reverse

    Reverse sort order.

.. option:: --style

    Table output style {fancy_grid,grid,html,latex,latex_booktabs,mediawiki,orgtbl,pipe,plain,psql,rst,simple,tsv}

    See the tabulate_ documentation for descriptions of the supported formats
    for your installation.

.. _tabulate: https://pypi.python.org/pypi/tabulate

.. option:: --help

    Show help message and exit.

``running``
'''''''''''

.. program:: rdial running

Display running task, if any

.. option:: --help

    Show help message and exit.

``last``
''''''''

.. program:: rdial last

Display last task, if any

.. option:: --help

    Show help message and exit.

``ledger``
''''''''''

.. program:: rdial ledger

Generate `ledger <http://ledger-cli.org/>`__ compatible data file

.. option:: -x, --from-dir

    Use directory name as task name.

.. option:: -d <duration>, --duration=<duration>

    Filter events for specified time period {day,week,month,year,all}.

.. option:: -r <rate>, --rate <rate>

    Hourly rate for task output.

.. option:: --help

    Show help message and exit.

BUGS
----

None known.

AUTHOR
------

Written by `James Rowe <mailto:jnrowe@gmail.com>`__

RESOURCES
---------

Full documentation: http://rdial.readthedocs.io/

Issue tracker: https://github.com/JNRowe/rdial/issues/

COPYING
-------

Copyright © 2011-2017  James Rowe.

rdial is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

rdial is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
rdial.  If not, see <http://www.gnu.org/licenses/>.
