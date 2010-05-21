#!/usr/bin/env python
'''
PdfPresenter - Software for presenting PDF slideshows on dual monitors.
By: Tom Wambold <tom5760@gmail.com>
'''

import sys
import os.path

import poppler
import gtk

class SlideWindow(gtk.Window):
    def __init__(self, document, page_number):
        super(SlideWindow, self).__init__()
        self.document = document
        self.page_number = page_number
        self.page = document.get_page(page_number)

        self.set_title(document.props.title)

        dwg = gtk.DrawingArea()
        dwg.connect('expose-event', self.on_expose)

        hbox = gtk.HBox()
        # The labels force the HBox to center the drawing area
        hbox.pack_start(gtk.Label(''), True, False)
        hbox.pack_start(dwg, False, False)
        hbox.pack_start(gtk.Label(''), True, False)

        self.add(hbox)

    def on_expose(self, widget, event):
        pwidth, pheight = self.page.get_size()
        wwidth, wheight = self.get_size()

        context = widget.window.cairo_create()

        # Scale and keep aspect ratio
        wscale = wwidth / pwidth
        hscale = wheight / pheight
        scale = wscale if wscale < hscale else hscale

        widget.set_size_request(pwidth * scale, pheight * scale)

        context.scale(scale, scale)
        self.page.render(context)

def main(argv):
    if len(argv) == 2:
        pdffile = argv[1]
    else:
        pdffile = 'demo_presentation/demo.pdf'

    path = 'file://' + os.path.abspath(pdffile)
    document = poppler.document_new_from_file(path, None)

    w1 = SlideWindow(document, 0)
    w2 = SlideWindow(document, 1)

    w1.connect('delete-event', gtk.main_quit)
    w2.connect('delete-event', gtk.main_quit)

    w1.show_all()
    w2.show_all()

    gtk.main()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
