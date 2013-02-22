Frequently Asked Questions
--------------------------

..
    Ask them, and perhaps they'll become frequent enough to be added here ;)

.. contents::

Why must I specify :option:`--new` when creating a new task
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Perhaps you're super special and never produce a typo, I'm not.  The
:option:`--new` option to :command:`rdial start` is a fix for this common -- to
me -- problem.

The :command:`rdial switch` command is of related design.  You can not use it
when no task is running, and attempting to do so is probably a sign you've lost
track of your state.  I consider this to be a massive problem, and would rather
not sidestep it by allowing :command:`rdial start` to stop running tasks.

Where does the name :program:`rdial` come from?
'''''''''''''''''''''''''''''''''''''''''''''''

Around the beginning of 2012 I wrote a very simple shell script to track my
time, and at some point I decided it should be safer and cleaner.  I came up
with a very clever and imaginative name for this new project, and then promptly
forgot how it came about.

Since then I haven't even managed to come up with a clever backronym for it.

.. Perhaps, Reducing Dedication In Actual Labour?
