#!/usr/bin/env python
'''
PdfPresenter - Software for presenting PDF slideshows on dual monitors.
By: Tom Wambold <tom5760@gmail.com>
'''

import sys
import os.path
from datetime import time 

import gtk
import gobject
import pango
import poppler

BACKGROUND_COLOR = '#000000'

class Timer(gtk.Label):
    def __init__(self):
        super(Timer, self).__init__()
        self.set_use_markup(True)
        self.started = False

    def start(self):
        self.cur_time = 0
        self.started = True
        gobject.timeout_add(1000, self.update_timer)

    def stop(self):
        self.started = False

    def update_timer(self):
        self.cur_time += 1
        timeobj = Timer.seconds_to_time(self.cur_time)
        self.set_markup('<span color="blue" size="xx-large">{0}</span>'.format(
            timeobj.strftime('%H:%M:%S')))
        return self.started

    @staticmethod
    def seconds_to_time(seconds):
        hours = seconds // 3600
        minutes = seconds // 60 % 60
        seconds = seconds - (3600 * hours) - (60 * minutes)
        return time(hours, minutes, seconds)

class SlideWindow(gtk.Window):
    def __init__(self, document, page_number, timer=None):
        super(SlideWindow, self).__init__()
        self.document = document
        self.page_number = page_number
        self.page = document.get_page(page_number)

        self.set_title(document.props.title)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BACKGROUND_COLOR))
        self.add_events(gtk.gdk.KEY_PRESS_MASK |
                        gtk.gdk.BUTTON_PRESS_MASK)

        self.drawing = gtk.DrawingArea()
        self.drawing.connect('expose-event', self.on_expose)

        hbox = gtk.HBox()
        # The labels force the HBox to center the drawing area
        hbox.pack_start(gtk.Label(''), True, False)
        hbox.pack_start(self.drawing, False, False)
        hbox.pack_start(gtk.Label(''), True, False)

        vbox = gtk.VBox()
        vbox.pack_start(hbox)

        if timer is not None:
            vbox.pack_start(timer)
            timer.start()

        self.add(vbox)

    def next_slide(self):
        self.set_cur_page(self.page_number + 2)

    def prev_slide(self):
        self.set_cur_page(self.page_number - 2)

    def set_cur_page(self, page_number):
        if page_number < 0 or page_number >= self.document.get_n_pages():
            return

        if page_number != self.page_number:
            self.page = self.document.get_page(page_number)
            self.page_number = page_number
            self.do_redraw()

    def on_expose(self, widget, event):
        self.do_redraw()

    def do_redraw(self):
        pwidth, pheight = self.page.get_size()
        wwidth, wheight = self.get_size()

        context = self.drawing.window.cairo_create()

        # Clear the page
        context.set_source_rgb(255, 255, 255)
        context.paint()

        # Scale and keep aspect ratio
        wscale = wwidth / pwidth
        hscale = wheight / pheight
        scale = wscale if wscale < hscale else hscale

        self.drawing.set_size_request(int(pwidth * scale), int(pheight * scale))

        # Draw the page
        context.scale(scale, scale)
        self.page.render(context)

class PdfPresenter(object):
    def __init__(self, pdf_path):
        pdf_path = 'file://' + os.path.abspath(pdf_path)
        self.document = poppler.document_new_from_file(pdf_path, None)

        self.main_window = SlideWindow(self.document, 0)
        self.note_window = SlideWindow(self.document, 1, Timer())

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
