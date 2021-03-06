#!/usr/bin/env python
'''
PdfPresenter - Software for presenting PDF slideshows on dual monitors.
By: Tom Wambold <tom5760@gmail.com>
'''

# Enable floating point division by default
from __future__ import division

import sys
import os.path
from datetime import time 

import gtk
import gobject
import poppler
import cairo

BACKGROUND_COLOR = '#000000'

class DocumentManager(object):
    'Maintains pre-rendered cairo surfaces to speed up drawing of pages.'

    def __init__(self, document, page_number=0):
        self.width = 0
        self.height = 0
        self.scale = 0

        self.document = document
        self.current_page = document.get_page(page_number)
        self.page_number = page_number

        self.pages = [None for x in xrange(document.get_n_pages())]

    def get_page_surface(self):
        page = self.pages[self.page_number]
        if page is None:
            self.pages[self.page_number] = page = self.render_page()
        return page

    def render_page(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                self.width, self.height)
        context = cairo.Context(surface)
        context.scale(self.scale, self.scale)
        self.current_page.render(context)

        return surface

    def draw_page(self, context):
        context.push_group()
        context.set_source_rgb(255, 255, 255)
        context.paint()
        context.set_source_surface(self.get_page_surface())
        context.paint()

        context.pop_group_to_source()
        context.paint()

    def get_scaled_size(self, width, height):
        pwidth, pheight = self.current_page.get_size()

        wscale = width / pwidth
        hscale = height / pheight
        self.scale = wscale if wscale < hscale else hscale

        new_width = int(pwidth * self.scale)
        new_height = int(pheight * self.scale)
        if new_width != self.width or new_height != self.height:
            self.invalidate_cache()

        self.width = new_width
        self.height = new_height
        return self.width, self.height

    def offset_page(self, offset):
        new_number = self.page_number + offset
        if new_number < 0 or new_number >= self.document.get_n_pages():
            return
        self.page_number = new_number
        self.current_page = self.document.get_page(new_number)

    def invalidate_cache(self):
        self.pages = [None for x in xrange(self.document.get_n_pages())]

class SlideWindow(gtk.Window):
    def __init__(self, manager, page_number=0):
        super(SlideWindow, self).__init__()
        self.manager = manager

        self.set_title(manager.document.props.title)
        #self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BACKGROUND_COLOR))
        self.add_events(gtk.gdk.KEY_PRESS_MASK |
                        gtk.gdk.BUTTON_PRESS_MASK)

        self.drawing = gtk.DrawingArea()
        self.drawing.connect('expose-event', self.on_expose)
        self.make_widgets()

    def make_widgets(self):
        self.add(self.drawing)

    def next_slide(self):
        self.manager.offset_page(2)
        self.do_redraw()

    def prev_slide(self):
        self.manager.offset_page(-2)
        self.do_redraw()

    def on_expose(self, widget, event):
        self.do_redraw()

    def do_redraw(self):
        self.drawing.set_size_request(*self.manager.get_scaled_size(*self.get_size()))
        self.manager.draw_page(self.drawing.window.cairo_create())

class NoteWindow(SlideWindow):
    def make_widgets(self):
        hbox = gtk.HBox()
        hbox.pack_start(self.drawing, True, True)

        vbox = gtk.VBox()

        label_box = gtk.HBox()
        label_box.add(gtk.Label('Time on slide:'))
        self.slide_time = gtk.Label('2:30')
        label_box.add(self.slide_time)
        vbox.add(label_box)

        label_box = gtk.HBox()
        label_box.add(gtk.Label('Total Time:'))
        self.total_time = gtk.Label('8:13')
        label_box.add(self.total_time)
        vbox.add(label_box)

        hbox.pack_start(vbox, False)
        self.add(hbox)

class PdfPresenter(object):
    def __init__(self, pdf_url):
        document = poppler.document_new_from_file(
                'file://' + os.path.abspath(pdf_url), None)

        self.main_window = SlideWindow(DocumentManager(document))
        self.note_window = NoteWindow(DocumentManager(document, 1))

        self.is_fullscreen = False

        for w in (self.main_window, self.note_window):
            w.connect('key-press-event', self.on_key_press)
            w.connect('button-press-event', self.on_button_press)
            w.connect('delete-event', gtk.main_quit)

    def run(self):
        self.main_window.show_all()
        self.note_window.show_all()
        gtk.main()

    def next_slide(self):
        self.main_window.next_slide()
        self.note_window.next_slide()

    def prev_slide(self):
        self.main_window.prev_slide()
        self.note_window.prev_slide()

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.main_window.unfullscreen()
            self.note_window.unfullscreen()
        else:
            self.main_window.fullscreen()
            self.note_window.fullscreen()
        self.is_fullscreen = not self.is_fullscreen

    def on_key_press(self, widget, event):
        if event.type != gtk.gdk.KEY_PRESS:
            return
        name = gtk.gdk.keyval_name(event.keyval)

        if name in ('Right', 'Down'):
            self.next_slide()
        elif name in ('Left', 'Up'):
            self.prev_slide()
        elif name == 'f':
            self.toggle_fullscreen()

    def on_button_press(self, widget, event):
        if event.type != gtk.gdk.BUTTON_PRESS:
            return

        if event.button == 1:
            self.next_slide()
        elif event.button == 3:
            self.prev_slide()

def main(argv):
    if len(argv) == 2:
        pdf_path = argv[1]
    else:
        pdf_path = 'demo_presentation/demo.pdf'

    p = PdfPresenter(pdf_path)
    p.run()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
