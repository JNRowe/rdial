:Author: James Rowe <jnrowe@gmail.com>
:Date: 2012-06-30
:Copyright: GPL v3
:Manual section: 1
:Manual group: user

rdial
======

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
    show program's version number and exit

-h, --help
    show program's help message and exit

-d <directory>, --directory=<directory>
    Database location, defaults to ``${XDG_DATA_HOME:-/.local}/rdial``

Commands
--------

``start``
'''''''''

Start task

-n, --new
   start a new task

-t <start time>, --time=<start time>
   manually set start time for task

-d, --from-dir
   use directory name as task

``stop``
''''''''

Stop task

-m <message>, --message=<message>
   closing message

--amend
   amend previous stop entry

``report``
''''''''''

Report time tracking data

-d <duration>, --duration=<duration>
   filter events for specified time period {day,week,month,year,all}

-s <order>, --sort=<order>
   field to sort by {task,time}

-r, --reverse
   reverse sort order

--html
   produce HTML output

--human
   produce human-readable output

-x, --from-dir
   use directory name as task

``running``
'''''''''''

Display running task, if any

``last``
''''''''

Display last task, if any

``ledger``
''''''''''

Generate `ledger <http://ledger-cli.org/>`__ compatible data file

-d <duration>, --duration=<duration>
   filter events for specified time period {day,week,month,year,all}

-r <rate>, --rate <rate>
   hourly rate for task output

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

Copyright © 2011-2012  James Rowe.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
