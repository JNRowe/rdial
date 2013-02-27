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

The configuration files are processed using Python's built-in
:mod:`~ConfigParser.SafeConfigParser`, and you can make use of all the features
it provides(such as interpolation).

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

This key sets the location of your data files.
