#
# Test for memory leak in screenshot.
#


from gi.repository import Wnck, Gtk, Gdk, GdkX11
import time


try:
    import Image
    import ImageChops
except:
    from PIL import Image
    from PIL import ImageChops

class ScreenShot():

    def __init__(self, title):
    
        self.title = title
        
        Gtk.init([]) # necessary only if not using a Gtk.main() loop

        self.window_handle = []
        self.window_handle.append(self.linux_get_windows_bytitle(self.title))
        w = self.window_handle[0]
        
    
    def linux_get_windows_bytitle(self, title_text, exact = False):
        """
        Finds a linux (Gtk) window by title. Returns window.
        """

        debug = False  
        
          
        screen = Wnck.Screen.get_default()
        screen.force_update()  # recommended per Wnck documentation

        window_list = screen.get_windows()

        if debug:
            for w in window_list:
                print w.get_name()
        
        if len(window_list) == 0:
            print "No Windows Found"
        for window in window_list:
            if exact:
                if window.get_name() == title_text:
                    return window
            else:
                if title_text in window.get_name():
                    return window
        
    def linux_screenshot(self, debug = False):
        """
        Takes a screenshot of the given window on linux using Gtk.
        """       
        
        w = self.window_handle[0]
        w.activate(int(time.time()))
        
        #Check to see if a window is above the target window
        if w.is_below():
            #If it is, don't bother taking a screen shot.
            return None
        
        w_xid = w.get_xid()
        w_gdk = GdkX11.X11Window.foreign_new_for_display(Gdk.Display.get_default(), w_xid)

        x, y, width, height = w.get_client_window_geometry()
        pb2 = Gdk.pixbuf_get_from_window(w_gdk, 0, 0, width, height)

        if (pb2 != None):            
            #width, height = pb2.get_width(),pb2.get_height()
            game_image = Image.fromstring("RGBA",(width,height),pb2.get_pixels() )
            #game_image.save("test.png", "png")
            #exit()
            return game_image
        else:
            print "Unable to get the screenshot."
    
if __name__ == "__main__":
    import resource
    import gc
    
    
    gameShot = ScreenShot("travis")
 
    #shot = linux_screenshot(window_handle[0], debug = False)

    for i in range(100000):
        shot = gameShot.linux_screenshot(debug = False)
        if i % 1000 == 0:
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            print("Cycles: {} \tMem: {}".format(i, mem))
