User-visible changes
====================

.. contents::

0.15.0 - 2016-01-12
-------------------

* Reading the database is now far faster!
* ``report``'s ``--human`` option has been renamed to ``--stats``
* unicodecsv_ is now required for Python 2 users
* User supplied datetime now support falling back to the system's ``date(1)``
  for parsing
* A cachedir_ tag is now created to help environments with cleaning tools
* Python 3.5 is officially supported
* Python 3.2 is no longer supported, but if you need it speak up!

.. _unicodecsv: https://crate.io/packages/unicodecsv/
.. _cachedir: http://www.brynosaurus.com/cachedir/

0.14.0 - 2014-06-10
-------------------

* Interactive message editing support has been added
* Many of the configuration options can now be set via envvars, for simple
  per-project setup
* Data caching has been added, and it significantly speeds up processing
* Python 3.4 is now supported
* Report generation now uses tabulate_, and supports many more output formats
  through that.  The prettytable_ dependency has been dropped
* ciso8601_ is now required, but does considerably speed up reading data files
* click_ is now required for command line parsing, and aaargh_ is no longer
  required
* configobj_ is now required
* blessings_ is no longer required

.. _ciso8601: https://crate.io/packages/ciso8601/
.. _click: https://crate.io/packages/click/
.. _configobj: https://crate.io/packages/configobj/
.. _tabulate: https://crate.io/packages/tabulate/

0.13.0 - 2014-02-05
-------------------

* Added new ``wrapper`` command for custom ``run`` shortcuts

0.12.0 - 2013-12-28
-------------------

* Add simple consistency checking subcommand ``fsck``
* Add subcommand to execute external command with timer ``run``

0.11.0 - 2013-03-13
-------------------

* Support specifying command defaults in config file, see ``doc/config.rst`` for
  details [#5]
* Support reading message text from a file with ``--file`` option
* *Massive* speed increase for users with large datastores [#8]
* Support for disabling data backups with the ``--no-backup`` option
* Pretty-ish icon for use in taskbars.  Better contributions welcome!
* isodate_ is no longer required

0.10.0 - 2013-02-22
-------------------

* The interface is becoming stable, and 1.0.0 release is likely imminent
* Added new ``switch`` command as shortcut for ``stop`` then ``start`` [#4]
* Tasks **must** not begin with a ``.``

0.9.0 - 2013-02-18
------------------

* When using the CLI the currently executing task is stored in ``.current``,
  so it can be used in status bars and such
* Backup data files are now stored in ``<taskname>.csv~``
* The API docs should hopefully be a lot clearer now thanks to many examples

0.8.0 - 2013-01-19
------------------

* blessings_ is now required
* ``--from-dir`` option has been added to ``report`` and ``ledger`` subcommands
* ``gettext`` support, submit your translations!
* Python 3.3 compatible [#3]

.. _blessings: https://crate.io/packages/blessings/

0.7.0 - 2012-10-17
------------------

* This may be the final minor release before version 1.0.0 is cut, please report
  any issues no matter how small you find!
* ``--from-dir`` option to ``start`` to set the task from the directory name

0.6.0 - 2012-10-05
------------------

* New ``last`` subcommand for showing the last event stored
* New tasks must now be accompanied by ``-new`` option when starting, this is
  to catch typos

0.5.0 - 2012-08-08
------------------

* Python 3 is now supported, and support for 2.5 has been dropped
* aaargh_ is now required [#1]
* zsh_ completion script in ``extra``
* pip_ requirements files in ``extra``

.. _aaargh: https://crate.io/packages/aaargh/
.. _zsh: http://www.zsh.org/
.. _pip: https://crate.io/packages/pip/

0.4.0 - 2012-07-03
------------------

* ``ledger`` subcommand to create output suitable for processing with ledger_
* ``--human`` option for ``report`` subcommand, with simpler output
* Initial user manual, using Sphinx_
* Tests now require nose2_ and expecter_, and ``behave`` is no longer required

.. _ledger: http://ledger-cli.org/
.. _Sphinx: http://sphinx.pocoo.org/
.. _nose2: https://crate.io/packages/nose2/
.. _expecter: https://crate.io/packages/expecter/

0.3.0 - 2012-02-16
------------------

* Storage now uses a file for each task, and should be significantly faster
* Installable using setuptools_
* ``report`` can now filter tasks by week
* Tests now require behave_, and ``lettuce`` is no longer required

.. _setuptools: https://crate.io/packages/distribute
.. _behave: https://crate.io/packages/behave/

0.2.0 - 2011-08-06
------------------

* Stop events can now have a message associated with them
* isodate_ is now required for date parsing, replacing the custom parser
* prettytable_ is now required for ``report`` output

.. _isodate: https://crate.io/packages/isodate/
.. _prettytable: http://code.google.com/p/prettytable/

0.1.0 - 2010-11-02
------------------

* Initial release
