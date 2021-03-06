Integrating with taskbars
=========================

The following sections should give you some idea of how you can (ab)use the
:file:`<database>/.current` file in your window manager of choice.

.. note::
   You’ll find exactly two examples right now, because these are the only two
   environments I use.  Feel free to submit your own!

..
   The idea here is show minimal examples, for the gist of the solution.  We
   want to see the principle not be flooded with the details.

.. todo::
   Add more fleshed out examples.

``awesomewm``
-------------

For example, with awesomewm_, you could create a simple timer based widget that
shows the running task:

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

.. _awesomewm: https://awesomewm.org/
.. _GFileMonitor: https://developer.gnome.org/gio/2.54/GFileMonitor.html
.. _signals: https://awesomewm.org/apidoc/classes/wibox.widget.textbox.html
.. _naughty: https://awesomewm.org/apidoc/libraries/naughty.html
.. _awful.button: https://awesomewm.org/apidoc/classes/awful.widget.button.html

``dwm``
-------

With dwm_ you’re basically free to pump the status bar however you wish.  If
you’re one of the users who likes to use a shell script to configure the bar,
then you can just :program:`cat` the :file:`.current` file from within your
script.

You could also edge towards mimicking the awesomewm_ configuration above with
the following genie_ snippet leveraging glib_:

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

You could also implement a simple task manager using dmenu_ or rofi_ to bind to
a key, the following zsh_ snippet shows how to build a selector for an existing
task:

.. code-block:: zsh

    tasks=(${XDG_DATA_HOME:-~/.local/share}/rdial/*~*~(:t:s/.csv/))
    rofi -dmenu -p "task?" <<< ${(F)tasks}

.. _dwm: http://dwm.suckless.org/
.. _genie: https://live.gnome.org/Genie
.. _glib: https://www.gtk.org/
.. _dmenu: http://tools.suckless.org/dmenu/
.. _rofi: https://github.com/DaveDavenport/rofi/
.. _zsh: http://www.zsh.org/

.. spelling::

    ab
    popup
    taskbars
