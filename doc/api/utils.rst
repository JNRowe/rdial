.. currentmodule:: rdial.utils

Utilities
=========

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`rdial`, and can be skipped if you are simply using the tool from the
  command line.

Convenience functions
'''''''''''''''''''''

.. autofunction:: write_current
.. autofunction:: remove_current

Time handling
'''''''''''''

.. autofunction:: parse_delta
.. autofunction:: format_delta
.. autofunction:: parse_datetime

.. autofunction:: utcnow

XDG Base Directory support
''''''''''''''''''''''''''

.. autofunction:: xdg_data_location

Text formatting
'''''''''''''''

.. autofunction:: _colourise
.. autofunction:: success
.. autofunction:: fail
.. autofunction:: warn

Examples
--------

Time handling
'''''''''''''

.. testsetup::

    import datetime

    from rdial.utils import (format_delta, parse_datetime, parse_delta)

.. doctest::
   :options: +NORMALIZE_WHITESPACE

    >>> parse_delta('PT36M10.951511S')
    datetime.timedelta(0, 2170, 951511)
    >>> parse_delta('')
    datetime.timedelta(0)
    >>> format_delta(datetime.timedelta(0))
    ''
    >>> format_delta(datetime.timedelta(minutes=30))
    'PT30M'
    >>> parse_datetime('2012-02-15T18:59:18Z')
    datetime.datetime(2012, 2, 15, 18, 59, 18, tzinfo=UTC())

XDG Base Directory support
''''''''''''''''''''''''''

.. testsetup::

    from rdial.utils import xdg_data_location

.. Don't run next test, as it is *entirely* system dependent

.. doctest::
   :options: +SKIP

    >>> xdg_data_location()
    '/home/jay/.xdg/local/rdial'

Text formatting
'''''''''''''''

.. need to figure out way to expose colouring in a sane manner

.. testsetup::

    from rdial.utils import (T, fail, success, warn)
    T._does_styling = False

.. doctest::

    >>> fail('Error!')
    'Error!'
    >>> success('Excellent')
    'Excellent'
    >>> warn('Ick')
    'Ick'
