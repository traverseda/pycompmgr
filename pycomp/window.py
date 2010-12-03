import struct, traceback

import xcb

import pycomp
import pycomp.render_util as render_util

class Window(object):
    def __init__(self, window):
        self.id = window
        self.attrs = pycomp.core.GetWindowAttributes(self.id)
        self.geom = pycomp.core.GetGeometry(self.id)
        self.update_opacity()

        self.pixmap = xcb.xproto.Pixmap._None
        self.picture = xcb.render.Picture._None
        self.alpha_pict = xcb.render.Picture._None

        self.damage = None
        self.damaged = False

        pycomp.stacking.append(self.id)
        pycomp.windows[self.id] = self

    def manage(self):
        if self.attrs._class != xcb.xproto.WindowClass.InputOnly:
            self.damage = pycomp.conn.generate_id()
            pycomp.damage.Create(
                self.damage,
                self.id,
                xcb.damage.ReportLevel.NonEmpty
            )

        if self.attrs.map_state == xcb.xproto.MapState.Viewable:
            self.listen()
            self.create_pixmap()
            self.fetch_opacity()

    def remove(self):
        self.damage = None

        if self.pixmap != xcb.xproto.Pixmap._None:
            self.free_pixmap()

        if self.damage:
            pycomp.damage.Destroy(self.damage)
            self.damage = None

        pycomp.stacking.remove(self.id)
        del pycomp.windows[self.id]

    def restack(self, new_above_window):
        pycomp.stacking.remove(self.id)

        if new_above_window not in pycomp.stacking:
            pycomp.stacking.insert(0, self.id)
        else:
            pycomp.stacking.insert(
                pycomp.stacking.index(new_above_window) + 1,
                self.id
            )

    def is_visible(self):
        g = self.geom

        return (
            g and
            g.x + g.width >= 1 and
            g.y + g.height >= 1 and
            g.x < pycomp.screen.width_in_pixels and
            g.y < pycomp.screen.height_in_pixels
        )

    def listen(self):
        pycomp.core.ChangeWindowAttributes(
            self.id,
            xcb.xproto.CW.EventMask,
            [xcb.xproto.EventMask.PropertyChange]
        )

    def fetch_attrs(self):
        if isinstance(self.attrs, xcb.Cookie):
            try:
                #self.attrs.check()
                self.attrs = self.attrs.reply()
            except:
                #traceback.print_exc()
                self.attrs = None
                return False

        return True

    def fetch_geometry(self):
        if isinstance(self.geom, xcb.Cookie):
            try:
                #self.geom.check()
                self.geom = self.geom.reply()
            except:
                #traceback.print_exc()
                self.geom = None
                return False

        return True

    def fetch_opacity(self):
        if isinstance(self.opacity, xcb.Cookie):
            try:
                #self.opacity.check()
                tmp = self.opacity.reply()

                tmpval = struct.unpack(
                    'I' * (len(tmp.value) / 4),
                    tmp.value.buf()
                )

                self.opacity = int(
                    (
                        float(tmpval[0]) / float(pycomp.OPAQUE)
                    ) * 0xffff
                )
            except:
                self.opacity = 0xffff
                return False

        return True

    def update_opacity(self):
        self.opacity = pycomp.core.GetProperty(
            False,
            self.id,
            pycomp._NET_WM_WINDOW_OPACITY,
            xcb.xproto.Atom.CARDINAL,
            0,
            1
        )

    def free_pixmap(self):
        if self.picture != xcb.render.Picture._None:
            pycomp.render.FreePicture(self.picture)
            self.picture = xcb.render.Picture._None

        pycomp.core.FreePixmap(self.pixmap)

    def create_alpha(self):
        pixmap = pycomp.conn.generate_id()
        pycomp.core.CreatePixmap(8, pixmap, pycomp.root, 1, 1)

        self.alpha_pict = pycomp.conn.generate_id()
        pycomp.render.CreatePicture(
            self.alpha_pict,
            pixmap,
            render_util.find_standard_format(
                pycomp.pict_formats,
                render_util.A_8
            ).id,
            xcb.render.CP.Repeat,
            [True]
        )

        pycomp.render.FillRectangles(
            xcb.render.PictOp.Src,
            self.alpha_pict,
            [0, 0, 0, self.opacity],
            1, # number of rectangles
            [0, 0, 1, 1]
        )

        pycomp.core.FreePixmap(pixmap)

    def create_picture(self):
        self.picture = pycomp.conn.generate_id()

        wvis = render_util.find_visual_format(
            pycomp.pict_formats,
            self.attrs.visual
        )

        pycomp.render.CreatePicture(
            self.picture,
            self.pixmap,
            wvis.format,
            xcb.render.CP.SubwindowMode,
            [xcb.xproto.SubwindowMode.ClipByChildren]
        )

    def create_pixmap(self):
        self.pixmap = pycomp.conn.generate_id()
        pycomp.composite.NameWindowPixmap(self.id, self.pixmap)

    def paint(self):
        render_composite_op = xcb.render.PictOp.Src
        if self.opacity is not None:
            render_composite_op = xcb.render.PictOp.Over

            if self.alpha_pict == xcb.render.Picture._None:
                self.create_alpha()

        pycomp.render.Composite(
            render_composite_op,
            self.picture,
            self.alpha_pict,
            pycomp.root_buffer_picture,
            0, 0, 0, 0,
            self.geom.x,
            self.geom.y,
            self.geom.width + self.geom.border_width * 2,
            self.geom.height + self.geom.border_width * 2
        )

    @staticmethod
    def paint_all():
        # Paint the windows in their proper stacking order
        for wid in pycomp.stacking:
            if wid not in pycomp.windows:
                continue

            w = pycomp.windows[wid]
            if not w.damage or not w.pixmap or not w.is_visible():
                continue

            # Paint the actual "window"...
            # If a picture doesn't exist (i.e., it was updated)
            # then re-create it
            if w.picture == xcb.render.Picture._None:
                w.create_picture()

            w.paint()
