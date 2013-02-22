Background
==========

I spend an awful lot of time sitting in front of a computer, working on a huge
number of disparate projects.  And when it comes time to gauge what I've been
working on it would be nice if I could just fire up a simple tool to see the
amount of time I'm spending on various tasks and projects.

The features *I* need in a time tracking tool are:

* Easily accessible data, in a format that can be processed simply
* Ability to work off-line, because those times are considerably more common
  than some people seem to think
* Works on all the platforms I regularly use; desktop, mobile phone, ZipIt, and
  more

Now :mod:`rdial` is born, and I should be able to realise those dreams!

Philosophy
----------

There are few interface choices in :program:`rdial` that may be need a little
explanation.  They may well be enough to deter you from using :program:`rdial`
at all, but that is fine there are :doc:`plenty more options <alternatives>` out
there!

Explicit new tasks
''''''''''''''''''

    It is an error to attempt to start a task that doesn't already exist in the
    database

If you wish to create a new task you *must* give the :option:`--new` option when
starting the task.  This should hopefully catch typos and task name "thinkos",
and it has proven to do so for me.

Switch vs "stopstart"
'''''''''''''''''''''

    It is an error to attempt to start a task when another is running, or
    switch a task when one is not running

If you wish to start a new task you *must* stop the previous one.  At first it
seems natural to just accept that :command:`rdial start` should complete the
previous task, but doing so encourages users to not be aware of their current
state.

Similarly, if you wish to switch to a new task then a task *must* be running.
It might be convenient to make :command:`rdial switch` just start the new task
if one is not running, but again it encourages users to be unaware of their
current state.
