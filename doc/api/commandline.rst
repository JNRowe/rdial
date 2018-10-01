.. module:: rdial.cmdline

Command line
============

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`rdial`, and can be skipped if you are simply using the tool from the
  command line.

Commands
~~~~~~~~

.. autofunction:: bug_data()
.. autofunction:: fsck(ctx, globs, progress)
.. autofunction:: start(globs, task, new, time)
.. autofunction:: stop(globs, message, fname, amend)
.. autofunction:: switch(globs, task, new, time, message, fname)
.. autofunction:: run(globs, task, new, time, message, fname, command)
.. autofunction:: wrapper(ctx, globs, time, message, fname, wrapper)
.. autofunction:: report(globs, task, stats, duration, sort, reverse, style)
.. autofunction:: running(globs)
.. autofunction:: last(globs)
.. autofunction:: ledger(globs, task, duration, rate)
.. autofunction:: timeclock(globs, task, duration, rate)

Entry points
~~~~~~~~~~~~~

.. autofunction:: cli(ctx, directory, backup, cache, config, interactive, colour)
.. autofunction:: main

Command support
~~~~~~~~~~~~~~~

.. autofunction:: filter_events
.. autofunction:: get_stop_message

CLI support
~~~~~~~~~~~

.. autoclass:: HiddenGroup
.. autoclass:: TaskNameParamType
.. autoclass:: StartTimeParamType

.. autofunction:: task_from_dir
.. autofunction:: task_option
.. autofunction:: duration_option
.. autofunction:: message_option
