# DF Everywhere
# Copyright (C) 2015  Travis Painter

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from sys import platform as _platform
import sys
import time

try:
    import Image
    import ImageChops
except:
    from PIL import Image
    from PIL import ImageChops
    
#Conditional Imports for windows/linux
if _platform.startswith("linux"):
    from gi.repository import Wnck, Gtk, Gdk, GdkX11
    Gtk.init([]) # necessary only if not using a Gtk.main() loop
elif _platform == "win32":
    import win32gui
    import win32ui
    from ctypes import windll

class ScreenShot():
    """
    Platform independent (windows/linux) screenshot tool for grabbing image of a single window. 
    """

    def __init__(self, title, exact = False, debug = False):
    
        self.title = title
        self.exact = exact
        self.debug = debug
        
        if _platform.startswith("linux"):
            self.get_window_by_title = self._linux_get_window_by_title
            self.get_screen_shot = self._linux_get_screenshot
        elif _platform == "win32":
            self.get_window_by_title = self._windows_get_window_by_title
            self.get_screen_shot = self._windows_get_screenshot
        else:
            # All others
            print("Unsupported platform detected. Exiting...")
            raw_input('Press [enter] to close this window.')
            sys.exit()
        
        
        self.window_handle = self.get_window_by_title(self.title, self.exact, self.debug)
        
    
    def _linux_get_window_by_title(self, title_text, exact = False, debug = False):
        """
        Finds a linux (wnck) window by title. Returns wnck window of first window found.
        [Linux Only]
        """
        
        screen = Wnck.Screen.get_default()
        screen.force_update()  # recommended per Wnck documentation

        window_list = screen.get_windows()

        if debug:
            for w in window_list:
                print("Window: {}".format(w.get_name()))
        
        if len(window_list) == 0:
            print "No Windows Found."
            raw_input('Press [enter] to close this window.')
            sys.exit()
        for window in window_list:
            if exact:
                if window.get_name() == title_text:
                    return window
            else:
                if title_text in window.get_name():
                    return window
                    
        #Error
        print("Window with given title not found.")
        print("Title: {}".format(title_text))
        raw_input('Press [enter] to close this window.')
        sys.exit()
    
    def _windows_get_window_by_title(self, title_text, exact = False, debug = False):    
        """
        Gets details of window position by title text. Returns window handle.
        [Windows Only]
        """   
        
        def _window_callback(hwnd, all_windows):
            all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
        
        window_list = []
        win32gui.EnumWindows(_window_callback, window_list)
        
        if debug:
            for w in window_list:
                print("Window: {}".format(w.get_name()))
        
        for hwnd, title in window_list:
            if exact:
                if title == title_text:
                    return hwnd
            else:
                if title_text in title:
                    return hwnd
            
        #Error
        print("Window with given title not found.")
        print("Title: {}".format(title_text))
        raw_input('Press [enter] to close this window.')
        sys.exit()
        
    def _linux_get_screenshot(self, debug = False):
        """
        Takes a screenshot of the given window on linux using Gtk.
        """       
        
        w = self.window_handle
        w.activate(int(time.time()))
        
        #Check to see if a window is above the target window
        if w.is_below():
            #If it is, don't bother taking a screen shot. There will be a missing portion.
            return None
        
        x, y, width, height = w.get_client_window_geometry()
        
        #Get xwindows id of wnck window
        w_xid = w.get_xid()
        #Use xwindows id to get a gdk window version
        w_gdk = GdkX11.X11Window.foreign_new_for_display(Gdk.Display.get_default(), w_xid)
        #Copy window image to new gdk pixelbuffer
        pb2 = Gdk.pixbuf_get_from_window(w_gdk, 0, 0, width, height)

        if (pb2 != None):
            shot = Image.fromstring("RGBA",(width,height),pb2.get_pixels() )
            if debug:
                shot.save("test.png", "png")
            return shot
        else:
            print "Unable to get screenshot."
            return None
            
    def _windows_get_screenshot(self, debug = False):
        """
        Takes a screenshot of the window on Windows. Will get image even if window is covered, but will fail if minimized.
        """
        
        hwnd = self.window_handle
        
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        w = right - left
        h = bot - top
        
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        
        saveDC.SelectObject(saveBitMap)
        
        result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
        
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        
        #If the window is minimized, no useful image data is received. Check this.
        #TODO: Should this just compare "result"?
        try:
            shot = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        except:
            print("Window must not be minimized. Also may happen if run from remote desktop.")
            result = 0
        
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        
        #PrintWindow Succeeded
        if result == 1:
            if debug:
                shot.save("test.png")
            return shot
        else:
            print "Unable to get screenshot."
            return None