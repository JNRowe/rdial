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

.. option:: -m <message>, --message=<message>
    Closing message.

.. option:: -F <file>, --file <file>
    Read closing message from file.

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

.. option:: -m <message>, --message <message>
    Closing message for current task.

.. option:: -F <file>, --file <file>
    Read closing message for current task from file.

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

.. option:: -m <message>, --message <message>
    Closing message for current task.

.. option:: -F <file>, --file <file>
    Read closing message for current task from file.

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

.. option:: -m <message>, --message <message>
    Closing message for current task.

.. option:: -F <file>, --file <file>
    Read closing message for current task from file.

.. option:: --help

    Show help message and exit.

``report``
''''''''''

.. program:: rdial report

Report time tracking data

.. option:: -d <duration>, --duration=<duration>
    Filter events for specified time period {day,week,month,year,all}.

.. option:: -s <order>, --sort=<order>
    Field to sort by {task,time}.

.. option:: -r, --reverse
    Reverse sort order.

.. option:: --style
    Table output style {grid,latex,mediawiki,orgtbl,pipe,plain,rst,simple,tsv}.

.. option:: --stats
    Display database statistics.

.. option:: -x, --from-dir
    Use directory name as task name.

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

.. option:: -d <duration>, --duration=<duration>
    Filter events for specified time period {day,week,month,year,all}.

.. option:: -r <rate>, --rate <rate>
    Hourly rate for task output.

.. option:: -x, --from-dir
    Use directory name as task name.

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

Home page, containing full documentation: http://rdial.rtfd.org/

Issue tracker: https://github.com/JNRowe/rdial/issues/

COPYING
-------

Copyright © 2011-2017  James Rowe.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
