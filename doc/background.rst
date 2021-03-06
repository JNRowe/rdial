Background
==========

I spend an awful lot of time sitting in front of a computer, working on many
disparate projects.  When I need to gauge my time it would be great if I could
just fire up a simple tool to see where I’ve been spending my time.

The features *I* need in a time tracking tool are:

* Easily accessible data, in a format that can be processed simply
* Ability to work off-line, because those times are considerably more common
  than some people seem to think
* Works on all the platforms I regularly use; desktop, mobile phone, ZipIt, and
  more

Now :mod:`rdial` is born, and I can realise those dreams!

Philosophy
----------

A few interface choices in :program:`rdial` may be need a little explanation.
Any one of them may well be enough to deter you from using :program:`rdial` at
all, but that is fine as :doc:`other options <alternatives>` are out there!

Explicit new tasks
~~~~~~~~~~~~~~~~~~

    It is an error to try to start a task that doesn’t already exist in the
    database

If you wish to create a new task you *must* give the :option:`rdial start
--new` option when starting the task.  This should — with hope — catch typos
and task name “thinkos”, and it has proven to do exactly that for me.

Switch vs “stopstart”
~~~~~~~~~~~~~~~~~~~~~

    It is an error to try to start a task when another is running, or switch
    a task when no task is running

If you wish to start a new task you *must* stop the previous task.  At first it
seems natural to just accept that :command:`rdial start` should complete the
previous task, but doing so encourages users to not be aware of their current
state.

Similarly, if you wish to switch to a new task then a task *must* be running.
It might be convenient to make :command:`rdial switch` just start the new task
if a task is not running, but again it encourages users to be unaware of their
current state.

.. spelling::

    stopstart
    thinkos
