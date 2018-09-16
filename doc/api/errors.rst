Errors
======

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`rdial`, and can be skipped if you are simply using the tool from the
  command line.

.. autoexception:: rdial.utils.RdialError

.. autoexception:: rdial.events.TaskNotRunningError
.. autoexception:: rdial.events.TaskRunningError

Examples
--------

.. testsetup::

    from rdial.events import (Events, TaskNotRunningError, TaskRunningError)
    events_running = Events()
    events_running.start('test', new=True)
    events_stopped = Events()

.. doctest::

    >>> events_stopped.stop()
    Traceback (most recent call last):
      …
    TaskNotRunningError: No task running!
    >>> events_running.start('rdial', new=True)
    Traceback (most recent call last):
      …
    TaskRunningError: Running task test!
