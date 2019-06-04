What is the future for :mod:`rdial`?
====================================

Where things stand :abbr:`now (2019-06-02)`:

.. code-block:: console

    $ time ./rdial.py --no-cache report --stats
    65726 events in query
    Duration of events 780 days, 14:04:22
    First entry started at 2011-12-15 14:02:13
    Last entry started at 2019-05-27 19:55:13.803240
    Events exist on 2659 dates
    Task “rdial” started 2019-05-27T19:55:13.803240Z
    ./rdial.py --no-cache report --stats  0.55s user 0.05s system 92% cpu 0.649 total

I’m clearly an extensive :mod:`rdial` user, and my inbox tells me that there
are fair number of other — hopefully happy — users too.  There are **no** plans
to stop working on it, but there are some thoughts about where it could go.

Data storage
------------

The output above is fairly representative of the speed of :command:`rdial` *for
me* [#]_.  All non-interactive commands run in well under three quarters of
a second, and with the cache enabled the commands run within half a second.
Performance *should* be better, but I find it to be within acceptable bounds.

One of the :doc:`original goals <background>` of :mod:`rdial` was “easily
accessible data, in a format that can be processed simply”.  The |CSV|-backed
storage is easy to work with, and performance is acceptable.  However, I’m more
than a little tempted to replace it with a sqlite_-backed solution because:

* ``sqlite`` is clearly a battle tested solution.
* Tests show performance improvements, although the large bottlenecks are in
  marshalling.
* The command line interface, :command:`sqlite`, can export in various formats
  (including |CSV|).
* It would remove the need for most of the chicanery around loading and saving
  of data, probably significantly improving the stability.
* A small number of the reports that I generate with :mod:`rdial` are actually
  performed by importing the data in to a ``sqlite`` in-memory database via its
  |CSV| support, which proves the suitability already.

:Likelihood: ✪✪✪✪○
:Effort: ✪✪○○○

Language
--------

I’m moderately happy with Python_ as the implementation language, although have
considered switching a couple of times to improve command response times.

Over the years I’ve re-implemented :mod:`rdial` to various extents when playing
with new languages:

.. list-table:: Possible implementation languages
   :header-rows: 1

   * - Language
     - Pros
     - Cons
   * - moonscript_
     - * Nice language
       * Fast runtime
       * lua_ is available *everywhere*
     - * No significant uptake
       * Annoying split between ``lua`` versions, and of course luajit_
       * Okay, not quite *everywhere* but close.
   * - nim_
     - * Fast runtime
       * Easy implementation
     - * Non-standard argument parsing, and no external package really fixes it
       * No significant uptake
       * Weak standard library, despite breadth
   * - rust_
     - * Fast runtime
       * Nice language
       * Good standard library
       * Common among co-worker users
     - * cargo_, while **amazing**, doesn’t fit my work environment very well
       * Doesn’t *currently* work on all the arches I use

.. note::

    While clearly not new languages, both Genie_ and ``C`` have been considered
    too.  ``Genie`` would be a good fit, but it is not clear what future it
    has.  ``C`` would basically be either a *huge* amount of work or a simple
    wrapper around existing libraries [#]_, neither of which I find compelling.

I’ve also considered the git_ approach, with a *fast* top-level wrapper
invoking external subcommands that could be in different languages.  This way
we can have *super* fast commands where they’re really needed(:command:`rdial
{start,stop,switch}`), and choose a feature appropriate language for other
commands(:command:`rdial report` for instance).  While attractive, it would
make packaging *far* more annoying.

:Likelihood: ✪✪○○○
:Effort: ✪✪✪✪✪

Interfaces
----------

A couple of users have expressed an interest in alternative interfaces, but I’m
not very enthusiastic about working on them myself.  I understand the desire,
but don’t feel it is worth the effort.  Added to that, if I’m not going to use
them myself, I’m probably not the best person to produce them.

That said, I do use :mod:`rdial` outside of the command line, but entirely by
wrapping the command line interface.  This feels like a reasonable solution,
but would benefit from a faster implementation and a *guaranteed* output
format.

So, *my* intention would be:

* Adding full documentation for my awesomewm_ integration.
* Open sourcing the Android Wear swipe integrations for my watch.
* A faster implementation.
* *Guaranteed* stable output format.

:Likelihood: ✪✪✪○○
:Effort: ✪✪✪○○

.. rubric:: Footnotes

.. [#] If you have info or views on *your* :command:`rdial` run times that
       you’d like to share I’d **love** to `hear them`_.
.. [#] At which point it provides *no benefits* over ``genie`` for me.

.. _sqlite: http://www.sqlite.org/
.. _python: http://www.python.org/
.. _moonscript: https://github.com/leafo/moonscript/
.. _lua: http://www.lua.org/
.. _luajit: http://luajit.org/
.. _nim: http://nim-lang.org/
.. _rust: http://www.rust-lang.org/
.. _cargo: https://crates.io/
.. _genie: https://live.gnome.org/Genie
.. _git: https://git-scm.com/
.. _awesomewm: http://awesomewm.org/
.. _hear them: jnrowe@gmail.com
