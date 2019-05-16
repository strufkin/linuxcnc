#!/usr/bin/env python
# vim: sts=4 sw=4 et
"""
XEmbed helper functions to allow correct embeding inside Axis
"""

#import gtk
import gi
from gi.repository import Gtk, Gdk

def reparent(window, parent):
    """ Forced reparent. When reparenting Gtk applications into Tk
    some extra protocol calls are needed.
    """
    from Xlib import display
    from Xlib.xobject import drawable

    if not parent:
        return window

    plug = Gtk.Plug.new(parent)
    plug.show()
    print(plug.get_property('window').get_xid())
    print(dir(plug.get_property('window')))
    print(dir(plug))
    #print(dir(plug.window))

    d = display.Display()
    # w = drawable.Window(d.display, plug.window.xid, 0)
    w = drawable.Window(d.display, plug.get_property('window').get_xid(), 0)
    # Honor XEmbed spec
    atom = d.get_atom('_XEMBED_INFO')
    w.change_property(atom, atom, 32, [0, 1])
    w.reparent(parent, 0, 0)
    w.map()
    d.sync()

    for c in window.get_children():
        window.remove(c)
        plug.add(c)

    # Hide window if it's displayed
    window.unmap()

    return plug

def keyboard_forward(window, forward):
    """ XXX: Keyboard events forwardind
        This is kind of hack needed to properly function inside Tk windows.
        Gtk app will receive _all_ events, even not needed. So we have to forward
        back things that left over after our widgets. Connect handlers _after_
        all others and listen for key-presss and key-release events. If key is not
        in ignore list - forward it to window id found in evironment.
    """
    print(forward)
    print(dir(forward))
    if not forward:
        return
    try:
        forward = int(forward, 0)
    except:
        return

    from Xlib.protocol import event
    from Xlib import display, X
    from Xlib.xobject import drawable

    d = display.Display()
    fw = drawable.Window(d.display, forward, 0)

    #ks = Gtk.keysyms
    #ignore = [ ks.Tab, ks.Page_Up, ks.Page_Down
    #         , ks.KP_Page_Up, ks.KP_Page_Down
    #         , ks.Left, ks.Right, ks.Up, ks.Down
    #         , ks.KP_Left, ks.KP_Right, ks.KP_Up, ks.KP_Down
    #         , ks.bracketleft, ks.bracketright
    #         ]
    ignore = [Gdk.KEY_Tab, Gdk.KEY_Page_Up, Gdk.KEY_Page_Down, Gdk.KEY_KP_Page_Up,Gdk.KEY_KP_Page_Down,Gdk.KEY_Left, Gdk.KEY_Left, Gdk.KEY_Up, Gdk.KEY_Down, \
            Gdk.KEY_KP_Left, Gdk.KEY_KP_Right, Gdk.KEY_KP_Up, Gdk.KEY_KP_Down, Gdk.KEY_bracketleft, Gdk.KEY_bracketright]

    def gtk2xlib(e, fw, g, type=None):
        if type is None: type = e.type
        if type == Gdk.EventType.KEY_PRESS:
            klass = event.KeyPress
        elif type == Gdk.EventType.KEY_RELEASE:
            klass = event.KeyRelease
        else:
            return
        kw = dict(window=fw, detail=e.hardware_keycode,
                  state=e.state & 0xff,
                  child=X.NONE, root=g._data['root'],
                  root_x=g._data['x'], root_y=g._data['y'],
                  event_x=0, event_y=0, same_screen=1)
        return klass(time=e.time, **kw)

    def forward(w, e, fw):
        if e.keyval in ignore:
            return

        g = fw.get_geometry()
        fe = gtk2xlib(e, fw, g)
        if not fe: return

        fw.send_event(fe)

    window.connect_after("key-press-event", forward, fw)
    window.connect("key-release-event", forward, fw)
    window.add_events(Gdk.EventMask.KEY_PRESS_MASK)
    window.add_events(Gdk.EventMask.KEY_RELEASE_MASK)
