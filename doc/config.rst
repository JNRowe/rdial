Configuration
=============

:program:`rdial` can be configured using a cascading series of files, processed
in the following order:

* The package's :file:`rdial/config` file which contains the base configuration
* Any :file:`rdial/config` file that exists in :envvar:`$XDG_CONFIG_DIRS`
* The user's :file:`rdial/config` file found in :envvar:`$XDG_CONFIG_HOME`
* The :file:`.rdialrc` found in the current directory

.. note::

   See the `XDG base directory specification`_ for more information on
   using :envvar:`$XDG_CONFIG_DIRS` and :envvar:`$XDG_CONFIG_HOME`.

.. _XDG base directory specification: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html

File format
-----------

The configuration file is a ``INI`` format file.  There is a section labelled
``rdial`` for global options, and a section for each subcommand.  Each section
consists of a section of ``name=value`` option pairs.

An example configuration file is below:

.. code-block:: ini

    [rdial]
    colour = False

    [report]
    sort = time
    reverse = True

The configuration files are processed using configobj_, and you can make use
of all the features it provides(such as interpolation).

.. _configobj: http://www.voidspace.org.uk/python/configobj.html

``rdial`` section
-----------------

``backup`` (default: ``True``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If this key is set to ``True`` then backup data files are written with a ``~``
suffix.

.. warning::

   You are strongly urged to keep this set to ``True``, as it helps to protect
   you from bugs in :mod:`rdial`.

``color`` (default: ``True``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If this key is set to ``False`` then no coloured output will be produced by
``rdial``.  You can also specify this for individual runs by setting the
:envvar:`NO_COLOUR` environment variable.

``directory`` (default: :file:`${XDG_DATA_HOME}/rdial`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This key sets the location of your data files.  Some users use this, combined
with the per-directory config file, to keep per-project task databases.

.. _run-wrappers-label:

``run wrappers`` section
------------------------

This section is used to configure pre-defined arguments for the :ref:`rdial run
<run-subcommand-label>` subcommand.  It consists of a series of string keys to
use as the wrapper title, and arguments to the :program:`rdial run` subcommand
as values.  For example:

.. code-block:: ini

    [run wrappers]
    feeds = -c 'mutt -f ~/Mail/RSS2email/' procast
    calendar = -c 'wyrd ~/.reminders/events' calendar

The above configuration entry ``feeds`` allows us to use ``rdial wrapper feeds``
to open ``mutt`` in a specific mailbox and time our usage under the ``procast``
task.
