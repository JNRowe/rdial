.. currentmodule:: rdial.cmdline

Command line
============

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`rdial`, and can be skipped if you are simply using the tool from the
  command line.

Commands
''''''''

.. autofunction:: fsck
.. autofunction:: start
.. autofunction:: stop
.. autofunction:: switch
.. autofunction:: run
.. autofunction:: wrapper
.. autofunction:: report
.. autofunction:: running
.. autofunction:: last
.. autofunction:: ledger

Entry points
'''''''''''''

.. autofunction:: cli
.. autofunction:: main

Command support
'''''''''''''''

.. autofunction:: filter_events
.. autofunction:: get_stop_message

CLI support
'''''''''''

.. autoclass:: TaskNameParamType
.. autoclass:: StartTimeParamType

.. autofunction:: task_from_dir
.. autofunction:: task_option
.. autofunction:: duration_option
.. autofunction:: message_option
