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

--version
    Show the version and exit.

-d <directory>, --directory=<directory>
    Database location, defaults to ``${XDG_DATA_HOME:-~/.local/share}/rdial``.

--backup/--no-backup
    Write data file backups.

--config <file>
    File to read configuration data from, defaults to
    ``${XDG_CONFIG_HOME:-~/.config}/rdial/config``.

--help
    Show help message and exit.

COMMANDS
--------

``fsck``
''''''''

Check storage consistency

--help
    Show help message and exit.

``start``
'''''''''

Start task

-x, --from-dir
    Use directory name as task name.

-n, --new
    Start a new task.

-t <time>, --time <time>
    Manually set start time for task.

--help
    Show help message and exit.

``stop``
''''''''

Stop task

-m <message>, --message=<message>
    Closing message.

-F <file>, --file <file>
    Read closing message from file.

--amend
    Amend previous stop entry.

--help
    Show help message and exit.

``switch``
''''''''''

Switch to another task

-x, --from-dir
    Use directory name as task name.

-n, --new
    Start a new task.

-m <message>, --message <message>
    Closing message for current task.

-F <file>, --file <file>
    Read closing message for current task from file.

--help
    Show help message and exit.

``run``
'''''''

Run command with timer

-x, --from-dir
    Use directory name as task name.

-n, --new
    Start a new task.

-t <time>, --time <time>
    Manually set start time for task.

-m <message>, --message <message>
    Closing message for current task.

-F <file>, --file <file>
    Read closing message for current task from file.

-c <command>, --command <command>
    Command to run.

--help
    Show help message and exit.

``wrapper``
'''''''''''

Run predefined command with timer

-t <time>, --time <time>
    Manually set start time for task.

-m <message>, --message <message>
    Closing message for current task.

-F <file>, --file <file>
    Read closing message for current task from file.

--help
    Show help message and exit.

``report``
''''''''''

Report time tracking data

-d <duration>, --duration=<duration>
    Filter events for specified time period {day,week,month,year,all}.

-s <order>, --sort=<order>
    Field to sort by {task,time}.

-r, --reverse
    Reverse sort order.

--html
    Produce HTML output.

--human
    Produce human-readable output.

-x, --from-dir
    Use directory name as task name.

--help
    Show help message and exit.

``running``
'''''''''''

Display running task, if any

--help
    Show help message and exit.

``last``
''''''''

Display last task, if any

--help
    Show help message and exit.

``ledger``
''''''''''

Generate `ledger <http://ledger-cli.org/>`__ compatible data file

-d <duration>, --duration=<duration>
    Filter events for specified time period {day,week,month,year,all}.

-r <rate>, --rate <rate>
    Hourly rate for task output.

-x, --from-dir
    Use directory name as task name.

--help
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

Copyright © 2011-2014  James Rowe.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
