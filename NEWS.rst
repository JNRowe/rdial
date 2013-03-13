User-visible changes
====================

.. contents::

0.11.0 - 2013-03-13
-------------------

* Support specifying defaults in config file, see ``doc/config.rst`` for details
* Support reading message text from a file with ``--file`` option
* *Massive* speed increase for users with large datastores
* Support for disabling data backups with the ``--no-backup`` option
* Pretty-ish icon for use in taskbars.  Better contributions welcome!
* isodate_ is no longer required

0.10.0 - 2013-02-22
-------------------

* The interface is becoming stable, and 1.0.0 release is likely imminent
* Added new ``switch`` command as shortcut for ``stop`` then ``start``
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
* Python 3.3 compatible

.. _blessings: http://pypi.python.org/pypi/blessings/

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
* aaargh_ is now required
* zsh_ completion script in ``extra``
* pip_ requirements files in ``extra``

.. _aaargh: http://pypi.python.org/pypi/aaargh/
.. _zsh: http://www.zsh.org/
.. _pip: http://pypi.python.org/pypi/pip/

0.4.0 - 2012-07-03
------------------

* ``ledger`` subcommand to create output suitable for processing with ledger_
* ``--human`` option for ``report`` subcommand, with simpler output
* Initial user manual, using Sphinx_
* Tests now require nose2_ and expecter_, and ``behave`` is no longer required

.. _ledger: http://ledger-cli.org/
.. _Sphinx: http://sphinx.pocoo.org/
.. _nose2: http://pypi.python.org/pypi/nose2/
.. _expecter: http://pypi.python.org/pypi/expecter/

0.3.0 - 2012-02-16
------------------

* Storage now uses a file for each task, and should be significantly faster
* Installable using setuptools_
* ``report`` can now filter tasks by week
* Tests now require behave_, and ``lettuce`` is no longer required

.. _setuptools: http://pypi.python.org/pypi/distribute
.. _behave: http://pypi.python.org/pypi/behave/

0.2.0 - 2011-08-06
------------------

* Stop events can now have a message associated with them
* isodate_ is now required for date parsing, replacing the custom parser
* prettytable_ is now required for ``report`` output

.. _isodate: http://pypi.python.org/pypi/isodate/
.. _prettytable: http://code.google.com/p/prettytable/

0.1.0 - 2010-11-02
------------------

* Initial release
