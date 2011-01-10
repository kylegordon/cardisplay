#!/usr/bin/env python

#PyCairoShape clock
#(c) 2007 Nicolas Trangez - ikke at nicolast dot be
#Released under GPL v2

#All imports we need
import sys
import gobject
import pango
import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk
import cairo
from datetime import datetime
import math

if gtk.pygtk_version < (2,10,0):
    print "PyGtk 2.10.0 or later required"
    raise SystemExit

#Yeah, globals. Warning: this code is messy
supports_alpha = False
win = None
shift_pressed = False
count = 0

#Our widget (window) is clicked
def clicked(widget, event):
    global win
    #If a shift key is pressed, start resizing
    if event.state & gtk.gdk.SHIFT_MASK:
            win.begin_resize_drag(gtk.gdk.WINDOW_EDGE_SOUTH_EAST, event.button, int(event.x_root), int(event.y_root), event.time)
    else:
    #else move
            win.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

#This is our main drawing function
def expose(widget, event):
    global supports_alpha

    (width, height) = widget.get_size()
    
    #Get a cairo context
    cr = widget.window.cairo_create()
    
    #Make the window transparent
    if supports_alpha == True:
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)
    else:
        cr.set_source_rgb(1.0, 1.0, 1.0) 
    
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.paint()

    #And draw everything we want
    #Some cos/sin magic is done, never mind
    cr.set_source_rgba(1.0, 0.2, 0.2, 0.7)
    if width < height:
        radius = float(width)/2 - 0.8
    else:
        radius = float(height)/2 - 0.8
        
    cr.arc(float(width)/2, float(height)/2, radius, 0, 2.0*3.14)
    cr.fill()
    cr.stroke()

    cr.move_to(float(width)/2, float(height)/2)
    if supports_alpha == True:
            cr.set_source_rgba(0.0, 0.0, 0.0, 0.9)
    else:
            cr.set_source_rgb(0.0, 0.0, 0.0)
    cr.set_line_width(0.05 * radius)
    cr.move_to(float(width)/2, float(height)/2)
    per_second = (2 * 3.14) / 60
    degrees = count * per_second
    degrees += 2 * 3.14 / 4
    cr.rel_line_to(-0.9 * radius * math.cos(degrees), -0.9 * radius * math.sin(degrees))
    cr.stroke()
   
    if supports_alpha == True:
            cr.set_source_rgba(0.5, 0.5, 0.5, 0.9)
    else:
            cr.set_source_rgb(0.5, 0.5, 0.5)
    cr.arc(float(width)/2, float(height)/2, 0.1 * radius, 0, 2.0*3.14)
    cr.fill()
    cr.stroke()

    #Once everything has been drawn, create our XShape mask
    #Our window content is contained inside the big circle,
    #so let's use that one as our mask
    pm = gtk.gdk.Pixmap(None, width, height, 1)
    pmcr = pm.cairo_create()
    pmcr.arc(float(width)/2, float(height)/2, radius, 0, 2.0*3.14)
    pmcr.fill()
    pmcr.stroke()
    #Apply input mask
    win.input_shape_combine_mask(pm, 0, 0)

    return False

#If screen changes, it could be possible we no longer got rgba colors
def screen_changed(widget, old_screen=None):
    
    global supports_alpha
    
    screen = widget.get_screen()
    colormap = screen.get_rgba_colormap()
    if colormap == None:
        print 'Your screen does not support alpha channels!'
        colormap = screen.get_rgb_colormap()
        supports_alpha = False
    else:
        print 'Your screen supports alpha channels!'
        supports_alpha = True
    
    widget.set_colormap(colormap)
    
    return True

#Queue a redraw of our window every second
def update_speedo():
    global win
    global count
    count = count + 1
    win.queue_draw()
    return True


#This should be obvious
def main(args):
    global win
    
    win = gtk.Window()

    # win.set_property("skip-taskbar-hint", True)
    
    win.set_title('PyCairoShape clock')
    win.connect('delete-event', gtk.main_quit)

    win.set_app_paintable(True)
    
    win.connect('expose-event', expose)
    win.connect('screen-changed', screen_changed)

    win.set_decorated(False)
    win.add_events(gdk.BUTTON_PRESS_MASK)
    win.connect('button-press-event', clicked)
    
    screen_changed(win)

    gobject.timeout_add(10, update_speedo)

    win.show_all()
    gtk.main()
    
    return True

if __name__ == '__main__':
    sys.exit(main(sys.argv))    

