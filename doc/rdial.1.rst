:Author: James Rowe <jnrowe@gmail.com>
:Date: 2012-06-30
:Copyright: GPL v3
:Manual section: 1
:Manual group: user

rdial
=====

Minimal time tracking for maximal benefit
-----------------------------------------

SYNOPSIS
--------

    rdial [option]… <command>

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

.. click:: rdial.cmdline:fsck
   :prog: rdial fsck

.. click:: rdial.cmdline:start
   :prog: rdial start

.. click:: rdial.cmdline:stop
   :prog: rdial stop

.. click:: rdial.cmdline:switch
   :prog: rdial switch

.. click:: rdial.cmdline:run
   :prog: rdial run

.. click:: rdial.cmdline:wrapper
   :prog: rdial wrapper

.. click:: rdial.cmdline:report
   :prog: rdial report

.. click:: rdial.cmdline:running
   :prog: rdial running

.. click:: rdial.cmdline:last
   :prog: rdial last

.. click:: rdial.cmdline:ledger
   :prog: rdial ledger

.. click:: rdial.cmdline:timeclock
   :prog: rdial timeclock

BUGS
----

None known.

AUTHOR
------

Written by `James Rowe <mailto:jnrowe@gmail.com>`__

RESOURCES
---------

Full documentation: https://rdial.readthedocs.io/

Issue tracker: https://github.com/JNRowe/rdial/issues/

COPYING
-------

Copyright © 2011-2019  James Rowe.

rdial is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

rdial is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
rdial.  If not, see <http://www.gnu.org/licenses/>.
