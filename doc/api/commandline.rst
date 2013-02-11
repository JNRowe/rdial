.. currentmodule:: rdial.cmdline

Command line
============

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`rdial`, and can be skipped if you are simply using the tool from the
  command line.

The ``args`` parameter in the functions below is an :class:`argparse.Namespace`
object, which is normally created in :func:`main`.

.. autofunction:: start
.. autofunction:: stop
.. autofunction:: report
.. autofunction:: running
.. autofunction:: last
.. autofunction:: ledger

.. autofunction:: main

.. autofunction:: filter_events
