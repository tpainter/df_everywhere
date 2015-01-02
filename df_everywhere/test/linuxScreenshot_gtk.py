#
# Uses PyGtk and wnck to get window and screenshot.
#
# Works.

import pygtk
pygtk.require('2.0')
import gtk, wnck
import gtk.gdk
import time

if __name__ == "__main__":
    default = wnck.screen_get_default()

    while gtk.events_pending():
        gtk.main_iteration(False)

    window_list = default.get_windows()
    DF_win = None

    if len(window_list) == 0:
        print "No Windows Found"
    for win in window_list:
        if win.is_active():
            print '***' + win.get_name()
        else:
            #print win.get_name()
            if win.get_name() == "Dwarf Fortress":
                DF_win = win

    if win is None:
        w = gtk.gdk.get_default_root_window()
    else:
        w = win

    root_win = gtk.gdk.get_default_root_window()

    print w.get_client_window_geometry()

    print "The size of the window is %d x %d" % (w.get_client_window_geometry()[2], w.get_client_window_geometry()[3])

    print "Activating window..."
    w.activate(int(time.time()))
    #Should not need to sleep, but works for now.
    time.sleep(1)

    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,w.get_client_window_geometry()[2], w.get_client_window_geometry()[3])
    pb = pb.get_from_drawable(root_win,root_win.get_colormap(),w.get_client_window_geometry()[0],w.get_client_window_geometry()[1],0,0,w.get_client_window_geometry()[2],w.get_client_window_geometry()[3])
    if (pb != None):
        pb.save("screenshot_gtk.png","png")
        print "Screenshot saved to screenshot_gtk.png."
    else:
        print "Unable to get the screenshot."