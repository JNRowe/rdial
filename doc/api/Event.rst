.. module:: rdial.events

``Event``
=========

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`rdial`, and can be skipped if you are simply using the tool from the
  command line.

.. autoclass:: Event
.. autoclass:: Events
.. autoclass:: RdialDialect

Examples
--------

.. testsetup::


    from rdial.events import (Event, Events)

.. doctest::

    >>> event = Event('test')
    >>> event.running()
    'test'
    >>> event.stop('complete')
    >>> event.running()
    False
    >>> data = event.writer()
    >>> data['message']
    'complete'
    >>> event2 = Event('test', start="2013-01-01T12:00:00Z")

    >>> events = Events([event, event2])
    >>> events.filter(lambda x: x.message == 'complete')
    Events([Event('test', '...', '...', 'complete')])
    >>> events.for_date(2013, 1)
    Events([Event('test', '2013-01-01T12:00:00Z', '', '')])
    >>> events.for_week(2012, 53)
    Events([Event('test', '2013-01-01T12:00:00Z', '', '')])
    >>> events.running()
    'test'
