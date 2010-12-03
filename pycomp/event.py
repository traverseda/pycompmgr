import time

import xcb

import pycomp
from pycomp.window import Window

paint = False
counter = 0

def get_window(e, attr='window'):
    if hasattr(e, attr):
        wid = getattr(e, attr)

        if (
            wid in pycomp.windows and
            pycomp.windows[wid].pixmap != xcb.xproto.Pixmap._None
        ):
            return pycomp.windows[wid]

    return None

def handle(e):
    global paint

    if isinstance(e, xcb.xproto.ConfigureNotifyEvent):
        w = get_window(e)
        if w is None:
            return

        w.geom.x = e.x
        w.geom.y = e.y
        if (
            w.geom.width != e.width or
            w.geom.height != e.height or
            w.geom.border_width != e.border_width
        ):
            w.free_pixmap()
            w.create_pixmap()

        w.geom.width = e.width
        w.geom.height = e.height
        w.geom.border_width = e.border_width
        w.geom.override_redirect = e.override_redirect

        w.restack(e.above_sibling)
    elif isinstance(e, xcb.xproto.CirculateNotifyEvent):
        w = get_window(e)
        if w is None:
            return

        if e.place == xcb.xproto.Place.OnBottom:
            w.restack(None)
        else:
            w.restack(pycomp.stacking[-1])
    elif isinstance(e, xcb.xproto.CreateNotifyEvent):
        w = Window(e.window)
        time.sleep(0.01)
        if not w.fetch_attrs() or not w.fetch_geometry():
            w.remove()
            return

        w.manage()
    elif isinstance(e, xcb.xproto.DestroyNotifyEvent):
        w = get_window(e, 'window')
        if w is None:
            return

        w.remove()
    elif isinstance(e, xcb.xproto.MapNotifyEvent):
        w = get_window(e, 'window')
        if w is None:
            return

        w.attrs.map_state = xcb.xproto.MapState.Viewable

        w.free_pixmap()
        w.create_pixmap()

        w.damaged = False
    elif isinstance(e, xcb.xproto.UnmapNotifyEvent):
        w = get_window(e)
        if w is None:
            return

        w.free_pixmap()

        w.attrs.map_state = xcb.xproto.MapState.Unmapped

        w.damaged = False
    elif isinstance(e, xcb.xproto.ReparentNotifyEvent):
        w = get_window(e)
        if e.parent == pycomp.root or w is None:
            w = Window(e.window)
            if not w.fetch_attrs() or not w.fetch_geometry():
                w.remove()
                return
            w.manage()
        elif w:
            w.remove()
    elif isinstance(e, xcb.xproto.PropertyNotifyEvent):
        w = get_window(e)
        if w is None:
            return

        if e.atom == pycomp._NET_WM_WINDOW_OPACITY:
            w.update_opacity()
            w.fetch_opacity()
            w.create_alpha()
    elif isinstance(e, xcb.damage.NotifyEvent):
        w = get_window(e, 'drawable')
        if w is None or not w.damage:
            return

        pycomp.damage.Subtract(
            w.damage,
            0,
            0
        )

        w.damaged = True
        paint = True
    else:
        print e
