Configuration
=============

.. highlight:: ini

:program:`rdial` can be configured using a cascading series of files, processed
in the following order:

* The package’s :file:`rdial/config` file which contains the base configuration
* Any :file:`rdial/config` file that exists in :envvar:`$XDG_CONFIG_DIRS`
* The user’s :file:`rdial/config` file found in :envvar:`$XDG_CONFIG_HOME`
* The :file:`.rdialrc` found in the current directory

.. note::

   See the `XDG base directory specification`_ for more information on
   using :envvar:`$XDG_CONFIG_DIRS` and :envvar:`$XDG_CONFIG_HOME`.

.. _XDG base directory specification: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html

File format
-----------

The configuration file is a ``INI`` format file.  Use a section labelled
``rdial`` for global options, and a separate section for each subcommand.  Each
section consists of a series of :samp:`name={value}` option pairs.

An example configuration file is below::

    [rdial]
    colour = False

    [report]
    sort = time
    reverse = True

The configuration files are processed using :mod:`configparser`, and you can
make use of all the features it provides(such as interpolation).

``rdial`` section
-----------------

``backup`` (default: ``True``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If this key is set to ``True`` then backup data files are written with a ``~``
suffix.

.. warning::

   You are strongly urged to keep this set to ``True``, as it helps to protect
   you from bugs in :mod:`rdial`.

``colour`` (default: ``True``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If this key is set to ``False`` then no coloured output will be produced by
``rdial``.

The key ``color`` is also accepted.

``directory`` (default: :file:`${XDG_DATA_HOME}/rdial`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This key sets the location of your data files.  Some users use this, combined
with the per-directory config file, to keep per-project task databases.

``interactive`` (default: ``False``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If this key is set to ``True`` then ``rdial`` will interactively ask the user
for for messages if they’re not supplied as arguments.

``run wrappers`` section
------------------------

This section is used to configure pre-defined arguments for the :program:`rdial
run` subcommand.  It consists of a series of string keys to use as the wrapper
title, and arguments to the :program:`rdial run` subcommand as values.  For
example::

    [run wrappers]
    feeds = -c 'mutt -f ~/Mail/RSS2email/' procrast
    calendar = -c 'wyrd ~/.reminders/events' calendar

The above configuration entry ``feeds`` allows us to use :samp:`rdial wrapper
{feeds}` to open ``mutt`` in a specific mailbox, and time our usage under the
ever popular ``procrast``-ination task.

.. spelling::

    ination
