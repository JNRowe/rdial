Alternatives
============

Before diving in and spitting out this package I looked at the alternatives
below.  If I have missed something please drop me a mail_.

It isn't meant to be unbiased, and you should try the packages out for yourself.
I keep it here mostly as a reference for myself, and maybe to help out people
who are already familiar with one of the entries below so they can see where I'm
coming from.

.. _mail: jnrowe@gmail.com

.. todo:: Check for recent additions to arena

``gtimelog``
------------

``gtimelog`` is an interesting tool, and ticks most of the boxes for me.  The
ideas are quite well thought out, and the interface is very simple to use.  I'm
sure it's great for people with strictly structured working days, but that
definitely isn't me.

As a side note, when we were playing with it at the office a number of
co-workers stumbled across various bugs that dogged its usage.  Unfortunately,
the project is developed with bzr and launchpad, so it was simply abandoned in
favour of trying to fix it.  Most moved on to ``org-mode``, and some to
``rdial``.

``hammertime``
--------------

hammertime_ is a great tool for tracking time in a simple manner, however it has
a couple of drawbacks for my use case.

Firstly, it stores data in a ``git`` branch which means all projects need their
own ``git`` repository.  This works surprisingly well for the most part,
but makes fetching all the stored data across multiple projects quite
cumbersome.

The more significant problem *for me* is that the implementation works by
stashing changes and switching branches, which will cause annoying rebuilds
every time you call ``git time``.  This could be fixed however by using ``git
hash-object`` directly for storing updates and ``git cat-file`` for reading
data, should anyone be interested in working on it.

I still happily recommend it to people who are simply trying to log the time
they spend working on small projects.

.. _hammertime: https://pypi.python.org/pypi/Hammertime/

``ktimetracker``
----------------

Works well, but isn't available on most of the platforms I care about.  If KDE
is available everywhere you care about, I'd heartily recommend it.

``org-mode``
------------

org-mode_ includes fantastic time tracking support, and some excellent reporting
mechanisms.  You can interleave your time tracking with other data, maintain
hierarchies of projects with their own time tracking data and take advantage of
all the other features ``org-mode`` has to offer.

If I had a copy of emacs_ available everywhere I wanted to log time data I
wouldn't even consider using anything else.  And if you use emacs_ then you
shouldn't either!

.. _org-mode: http://www.orgmode.org/
.. _emacs: http://www.gnu.org/software/emacs/

``taskwarrior``
---------------

There is some support for time tracking in taskwarrior_, and if you only need to
maintain a log of the time you spend on previously defined tasks it is probably
enough to get by.

I still take advantage of its functionality now, in combination with ``rdial``,
so that I can see when I started working toward a task in my to-do list.

.. _taskwarrior: http://taskwarrior.org/
