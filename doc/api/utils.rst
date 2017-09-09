.. currentmodule:: rdial.utils

Utilities
=========

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`rdial`, and can be skipped if you are simply using the tool from the
  command line.

Convenience functions and classes
'''''''''''''''''''''''''''''''''

.. autofunction:: write_current
.. autofunction:: remove_current

.. autofunction:: newer
.. autofunction:: term_link

Time handling
'''''''''''''

.. autofunction:: parse_datetime_user

Examples
--------

Time handling
'''''''''''''

.. testsetup::

    from rdial.utils import parse_datetime_user

.. doctest::
   :options: +SKIP

    >>> parse_datetime_user('40 minutes ago')
    datetime.datetime(2012, 2, 15, 18, 59, 18)
