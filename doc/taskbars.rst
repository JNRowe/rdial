Integrating with taskbars
=========================

The following sections should give you some idea of how you can (ab)use the
:file:`.current` file in your window manager of choice.

.. note::
   There are exactly two examples right now, because these are the two
   environments I use.  Feel free to submit your own!

..
   The idea here is show minimal examples, for the gist of the solution.  We
   want to see the principal not be flooded with the details.

.. todo::
   Add more fleshed out examples.

``awesome``
-----------

For example, with awesome_, you could create a simple timer based widget that
shows the currently running task:

.. code-block:: moon

    GLib = lgi.GLib
    tasktext = wibox.widget.textbox!
    tasktimer = with gears.timer timeout: 30
        \connect_signal "timeout", ->
            if file = io.open GLib.get_user_data_dir! .. "/rdial/.current"
                tasktext\set_markup file\read!
                file\close!
            else
                tasktext\set_markup "none"
        -- fire timer for initial update
        \emit_signal "timeout"
        \start!

.. note::
   The above example is compact but very naïve, and will be incorrect in the
   time between state changes and updates.  If you’re implementing your own
   widget you’ll be better served by using GFileMonitor_ to track state changes.

You could also hook the ``mouse::enter`` and ``mouse::leave`` signals_ to create
a naughty_ popup showing the task time, or use awful.button_ to allow you to
switch tasks directly from the taskbar.

.. _awesome: http://awesome.naquadah.org/
.. _GFileMonitor: https://developer.gnome.org/gio/2.32/GFileMonitor.html
.. _signals: http://awesome.naquadah.org/wiki/Signals
.. _naughty: http://awesome.naquadah.org/doc/api/modules/naughty.html
.. _awful.button: http://awesome.naquadah.org/doc/api/modules/awful.button.html

``dwm``
-------

With dwm_ you’re basically free to pump the status bar however you wish.  You
could, for example, just show the current task with the following genie_
snippet:

.. code-block:: vala

    [indent=4]

    uses
        X
        Posix

    init
        var file = GLib.Environment.get_user_data_dir() + "/rdial/.current"
        var dpy = new X.Display()
        var root = dpy.default_root_window()
        text : string

        while true
            if GLib.FileUtils.test(file, GLib.FileTest.IS_REGULAR)
                GLib.FileUtils.get_contents(file, out text)
            else
                text = "none"
            dpy->change_property(root, XA_WM_NAME, XA_STRING, 8,
                                 PropMode.Replace, (array of uchar)text,
                                 text.length)
            dpy->flush()
            Posix.sleep(30)

.. note::
   The above example is compact but very naïve, and will be incorrect in the
   time between state changes and updates.  If you’re implementing your own
   status tool you’ll be better served by using GFileMonitor_ to track state
   changes.

You could also implement a simple task manager using dmenu_, the following
zsh_ snippet shows how to build a selector for an existing task:

.. code-block:: sh

    echo ${XDG_DATA_HOME:-~/.local/share}/rdial/*~*~(:t:s/.csv/) |
        tr ' ' '\n' |
        dmenu -p "task?"

.. _dwm: http://dwm.suckless.org/
.. _genie: https://live.gnome.org/Genie
.. _dmenu: http://tools.suckless.org/dmenu/
.. _zsh: http://www.zsh.org/

