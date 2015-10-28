#
# Test for memory leak in screenshot.
#

import gtk, wnck
import gtk.gdk
import time
import gc

try:
    import Image
    import ImageChops
except:
    from PIL import Image
    from PIL import ImageChops

def linux_get_windows_bytitle(title_text, exact = False):
    """
    Finds a linux (Gtk) window by title. Returns window.
    """

    debug = False
 
    default = wnck.screen_get_default()

    while gtk.events_pending():
        gtk.main_iteration(False)

    window_list = default.get_windows()
    
    if debug:
        for w in window_list:
            print w.get_name()
    
    if len(window_list) == 0:
        print "No Windows Found"
    for win in window_list:
        if exact:
            if win.get_name() == title_text:
                return win
        else:
            if title_text in win.get_name():
                return win
    
def linux_screenshot(wnck_win = None, debug = False):
    """
    Takes a screenshot of the given window on linux using Gtk.
    """
    
    
    root_win = gtk.gdk.get_default_root_window()
    w = wnck_win
    w.activate(int(time.time()))
    #Should not need to sleep, but works for now.
    #time.sleep(1)
    #Maybe just needs a flush()?
    
    #Check to see if a window is above the target window
    if w.is_below():
        #If it is, don't bother taking a screen shot.
        return None

    pb1 = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,w.get_client_window_geometry()[2], w.get_client_window_geometry()[3])
    pb2 = pb1.get_from_drawable(root_win,root_win.get_colormap(),w.get_client_window_geometry()[0],w.get_client_window_geometry()[1],0,0,w.get_client_window_geometry()[2],w.get_client_window_geometry()[3])
    if (pb2 != None):
        if debug:
            pb2.save("screenshot_gtk.png","png")
            print "Screenshot saved to screenshot_gtk.png."
        
        width, height = pb2.get_width(),pb2.get_height()
        game_image = Image.fromstring("RGB",(width,height),pb2.get_pixels() )
        #See: http://faq.pygtk.org/index.py?req=show&file=faq08.004.htp for method to avoid memory leak.
        
        del pb1
        del pb2
        del root_win
        del wnck_win
        del w
        gc.collect()
        
        return game_image
    else:
        del pb1
        del pb2
        del root_win
        del wnck_win
        del w
        gc.collect()
        print "Unable to get the screenshot."
    
if __name__ == "__main__":
    import resource
    import gc
    
    window_handle = []
    window_handle.append(linux_get_windows_bytitle("travis"))
 
    #shot = linux_screenshot(window_handle[0], debug = False)

    for i in range(100000):
        shot = linux_screenshot(window_handle[0], debug = False)
        if i % 1000 == 0:
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            print("Cycles: {} \tMem: {}".format(i, mem))
        del shot
        gc.collect()
