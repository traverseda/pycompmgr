import xcb, xcb.xproto, xcb.render, xcb.composite, xcb.damage
import render_util

OPAQUE = 0xffffffff

conn = xcb.xcb.connect()
render = conn(xcb.render.key)
composite = conn(xcb.composite.key)
damage = conn(xcb.damage.key)

damage_check = damage.QueryVersion(
    xcb.damage.MAJOR_VERSION,
    xcb.damage.MINOR_VERSION
).reply()

core = conn.core
setup = conn.get_setup()

screen = setup.roots[0]
root = screen.root

root_visual = screen.root_visual
pict_formats = render.QueryPictFormats().reply()
pictvisual = render_util.find_visual_format(pict_formats, root_visual)

root_picture = xcb.render.Picture._None
root_buffer_picture = xcb.render.Picture._None
background_picture = xcb.render.Picture._None

_NET_WM_WINDOW_OPACITY = core.InternAtom(
    False,
    len('_NET_WM_WINDOW_OPACITY'),
    '_NET_WM_WINDOW_OPACITY'
).reply().atom

query_tree = conn.core.QueryTree(root).reply().children

windows = {}
stacking = []

def sync():
    core.GetInputFocus().reply()

def paint_background():
    global root_picture, root_buffer_picture, background_picture

    # Create a picture of the root window
    root_picture = conn.generate_id()
    render.CreatePicture(
        root_picture,
        root,
        pictvisual.format,
        xcb.render.CP.SubwindowMode,
        [xcb.xproto.SubwindowMode.IncludeInferiors]
    )

    # Start buffer creation
    # Create a pixmap of the root window for a buffer
    # This prevents us from painting directly to the root
    # window every time we composite something to the
    # screen. (Thus preventing a "flicker" effect.)
    pixmap = conn.generate_id()
    conn.core.CreatePixmap(
        screen.root_depth,
        pixmap,
        root,
        screen.width_in_pixels,
        screen.height_in_pixels
    )

    # Now create a picture of that pixmap.
    root_buffer_picture = conn.generate_id()
    render.CreatePicture(
        root_buffer_picture,
        pixmap,
        pictvisual.format,
        0,
        []
    )
    conn.core.FreePixmap(pixmap)
    # End buffer creation

    # Begin background picture creation
    pixmap = conn.generate_id()
    conn.core.CreatePixmap(
        screen.root_depth,
        pixmap,
        root,
        1,
        1
    )

    background_picture = conn.generate_id()
    render.CreatePicture(
        background_picture,
        pixmap,
        pictvisual.format,
        xcb.render.CP.Repeat,
        [True]
    )
    conn.core.FreePixmap(pixmap)

    render.FillRectangles(
        xcb.render.PictOp.Src,
        background_picture,
        [0x8080, 0x8080, 0x8080, 0xffff], # grey
        1, # 1 rectangle
        [0, 0, screen.width_in_pixels, screen.height_in_pixels]
    )
    # End background picture creation

    # Composite the background picture on to the buffer
    paint_background_to_buffer()

    # Now wrap it up by compositing the buffer on to the
    # actual root window
    paint_buffer()

def paint_background_to_buffer():
    render.Composite(
        xcb.render.PictOp.Src,
        background_picture,
        0,
        root_buffer_picture,
        0, 0, 0, 0, 0, 0,
        screen.width_in_pixels,
        screen.height_in_pixels
    )

def paint_buffer():
    render.Composite(
        xcb.render.PictOp.Src,
        root_buffer_picture,
        0,
        root_picture,
        0, 0, 0, 0, 0, 0,
        screen.width_in_pixels,
        screen.height_in_pixels
    )
