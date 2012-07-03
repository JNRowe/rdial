User-visible changes
====================

.. contents::

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
