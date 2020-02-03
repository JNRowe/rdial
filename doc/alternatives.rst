Alternatives
============

Before diving in and spitting out this package I looked at the alternatives
below.  If I have missed something please drop me a mail_.

It isn’t meant to be unbiased, and you should try the packages out for
yourself.  I keep it here mainly as a reference for myself, and maybe to help
out people who are already familiar with one of the entries below.

.. _mail: jnrowe@gmail.com

.. todo:: Check for recent additions to the arena.

``arbtt``
---------

The “Automatic Rule-Based Time Tracker”, where automatic could equally be
awesome.  You run the daemon and it records yours tasks automatically.  The
rules to configure switching are easy to write, and depending on your needs may
well catch all your task switching.

It only falls down when you need to record tasks which aren’t 100% about
whacking away at the keyboard in a window, so if your time tracking needs are
*entirely* screen based I recommend you try it out.

.. _arbtt: http://hackage.haskell.org/package/arbtt

``gtimelog``
------------

``gtimelog`` is an interesting tool, and ticks many of the boxes for me.  The
ideas are quite well thought out, and the interface is simple to use.  I’m sure
it’s great for people with strictly structured working days, but that
definitely isn’t me.

As a side note, when we were playing with it at the office several of my
co-workers stumbled across various bugs that dogged its usage.  Unfortunately,
the project is developed with bzr and launchpad, therefore it was simply
abandoned in favour of trying to fix it.  Most moved on to ``org-mode``, and
some to ``rdial``.

``hammertime``
--------------

hammertime_ is a great tool for tracking time in a simple manner, however it
has a couple of drawbacks for my use case.

First, it stores data in a ``git`` branch which means all projects need their
own ``git`` repository.  This works surprisingly well for the most part, but
makes fetching all the stored data across multiple projects quite cumbersome.

The more significant problem *for me* is that the implementation works by
stashing changes and switching branches, which will cause annoying rebuilds
every time you call ``git time`` if you’re using a time based build tool like
:program:`make`.  However, this could fixed by using ``git hash-object``
directly for storing updates and ``git cat-file`` for reading data, should
anyone be interested in working on it.

I still happily recommend it to people who are simply trying to log the time
spent working on small projects.

.. _hammertime: https://pypi.org/project/Hammertime/

``hamster-time-tracker``
------------------------

ProjectHamster_ and its associated clients are a neat solution to time
tracking.  The gnome applet and command line interface are particularly
polished.  The :command:`hamster-cli` in particular is extremely nice to use,
and the built-in :abbr:`DWIM (Do What I Mean)` date handling provides some
great shortcuts for adding missing entries.

The data backend is a simple SQLite_ database, and is therefore very amenable
to external processing.  It provides tagging on top of the fields provided
by :command:`rdial`, and that alone may make it more useful to you.

.. _ProjectHamster: http://projecthamster.org/
.. _SQLite: http://www.sqlite.org/

``ktimetracker``
----------------

Works well, but isn’t available on most of the platforms I care about.  If KDE
is available everywhere you care about, I’d heartily recommend it.

``org-mode``
------------

org-mode_ includes fantastic time tracking support, and some excellent reporting
mechanisms.  You can interleave your time tracking with other data, maintain
hierarchies of projects with their own time tracking data and take advantage of
all the other features ``org-mode`` has to offer.

If I had a copy of emacs_ available everywhere I wanted to log time data I
wouldn’t even consider using anything else.  And if you use emacs_ then you
shouldn’t either!

.. _org-mode: http://www.orgmode.org/
.. _emacs: http://www.gnu.org/software/emacs/

``taskwarrior``
---------------

taskwarrior_ has some support for time tracking, and if you only need to
maintain a log of the time you spend on previously defined tasks it is probably
enough to get by.

I still take advantage of its functionality now, in combination with ``rdial``,
so that I can see when I started working toward a task in my to-do list.

.. _taskwarrior: http://taskwarrior.org/

``timewarrior``
---------------

From the same stable as taskwarrior_, timewarrior_ is an *excellent* solution
for time tracking.  It doesn’t support close messages, but it does have amazing
tag support and some really useful query options.

There are import and export scripts in the ``extra`` subdirectory, and I truly
recommend trying timewarrior_ out.

The only possible drawback is its speed, as with large numbers of records its
startup becomes *very* slow.  Exporting my eight year :command:`rdial`
database results in three second pauses on each :command:`timew` run.

.. note::

    This *may* be fixed in future releases, see timewarrior’s issue
    tracker(`#245`_ and `#269`_) for more information and possible fixes.

.. _timewarrior: https://taskwarrior.org/news/news.20160821.html
.. _#245: https://github.com/GothenburgBitFactory/timewarrior/issues/245
.. _#269: https://github.com/GothenburgBitFactory/timewarrior/pull/269

.. spelling::

    backend
    bzr
    startup
