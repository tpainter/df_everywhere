# DF Everywhere
# Copyright (C) 2014  Travis Painter

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

try:
    import Image
    import ImageChops
except:
    from PIL import Image
    from PIL import ImageChops

import os
    

def win_get_windows_bytitle(title_text, exact = False):    
    """
    Gets details of window position by title text. [Windows Only]
    """   
    
    import win32gui
    
    def _window_callback(hwnd, all_windows):
        all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    windows = []
    win32gui.EnumWindows(_window_callback, windows)
    if exact:
        return [hwnd for hwnd, title in windows if title_text == title]
    else:
        return [hwnd for hwnd, title in windows if title_text in title]
        
def win_screenshot(hwnd = None, debug = False):
    """
    Takes a screenshot of only the area given by the window.
    """   
    
    import win32gui
    import win32ui
    from ctypes import windll
     
    if not hwnd:
        print("Unable to get window. Exiting.")
        exit()
    
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
    
    #If the window is minimized, no useful image data is received. Check this
    try:
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
    except:
        print("Dwarf Fortress window must not be minimized.")
        result = 0
    
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        #PrintWindow Succeeded
        #img.save("test.png")
        return img      
    
        
def win_screenshot_old(hwnd = None, debug = False):
    """
    Takes a screenshot of only the area given by the window.
    """
    #Windows only - get screenshot of window instead of whole screen
    # from: https://stackoverflow.com/questions/3260559/how-to-get-a-window-or-fullscreen-screenshot-in-python-3k-without-pil
    
    import win32con
    import win32gui
        
    if not hwnd:
        print("Unable to get window. Exiting.")
        exit()
    
    bbox_total = win32gui.GetWindowRect(hwnd)
    bbox_client = win32gui.GetClientRect(hwnd) #window without the title bar, but in 'local' window coordinates
    
    #win32gui.SetForegroundWindow(hwnd)
    # Move window to top (i.e. "ensure that it is not coverd") without giving it focus.
    flags = win32con.SWP_NOACTIVATE
    
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, bbox_total[0], bbox_total[1], bbox_total[2] - bbox_total[0], bbox_total[3] - bbox_total[0], flags)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, bbox_total[0], bbox_total[1], bbox_total[2] - bbox_total[0], bbox_total[3] - bbox_total[0], flags)
    
    
    #bbox points are [start_x, start_y, stop_x, stop_y]
    #added extra number to make it work on my system... need to look into this - seems to be a 4px border
    diff_x = (bbox_total[2] - bbox_total[0]) - bbox_client[2] - 4
    diff_y = (bbox_total[3] - bbox_total[1]) - bbox_client[3] - 4
    bbox = [bbox_total[0] + diff_x, bbox_total[1] + diff_y, bbox_total[0] + diff_x + bbox_client[2], bbox_total[1] + diff_y + bbox_client[3]] 
    #sleep(.2) #wait for window to be brought to front
    img = ImageGrab.grab(bbox)
    
    if debug:
        print("Whole window:")
        print(bbox_total)
        print("Client area:")
        print(bbox_client)
        print("Modified box:")
        print(bbox)
    
        filename = "aa_image.png"
        img.save(filename)
        #import webbrowser
        #webbrowser.open(filename)
    
    return img
    
def linux_get_windows_bytitle(title_text, exact = False):
    """
    Finds a linux (Gtk) window by title. Returns window.
    """
    
    import gtk, wnck
 
    default = wnck.screen_get_default()

    while gtk.events_pending():
        gtk.main_iteration(False)

    window_list = default.get_windows()

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
    
    import gtk, wnck
    import gtk.gdk
    import time
    
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

    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,w.get_client_window_geometry()[2], w.get_client_window_geometry()[3])
    pb = pb.get_from_drawable(root_win,root_win.get_colormap(),w.get_client_window_geometry()[0],w.get_client_window_geometry()[1],0,0,w.get_client_window_geometry()[2],w.get_client_window_geometry()[3])
    if (pb != None):
        if debug:
            pb.save("screenshot_gtk.png","png")
            print "Screenshot saved to screenshot_gtk.png."
        
        width, height = pb.get_width(),pb.get_height()
        return Image.fromstring("RGB",(width,height),pb.get_pixels() )
    else:
        print "Unable to get the screenshot."
    
def findLocalImg(x, y):
    """
    Try to find the best local tileset based on tile dimensions
    """
    
    
    fileList = []
    filePrefix = "%02dx%02d-" % (x, y)
    
    for file in os.listdir("./tilesets/"):
        if file.endswith(".png"):
            if file.startswith(filePrefix):
                fileList.append((int(file[6:11]), file))
    
    #sort by number of tiles in tileset
    fileList_sorted = sorted(fileList, key=lambda tup: tup[0], reverse = True)
    
    if fileList == []:
        print("Didn't find appropriate tileset image. Continuing")
        return None
    else:
        print("Found tileset image: %s" % fileList_sorted[0][1])
        return fileList_sorted[0][1]
        
def findTileSize(img):
    """
    Tries to automatically find the tile size
    """
    
    #start with 16x16 tile
    initial_guess = 16
    
    tile_x = initial_guess
    tile_y = initial_guess
    px, py = img.size
    
    #The tiles should be square
    for x in range(initial_guess, 0, -1):
        if (px % x == 0) and (py % x == 0):
            tile_x = x
            tile_y = x
            break
        else:
            continue
    
    print("Tile size found: %dx%d" % (tile_x, tile_y))
    if tile_x < 7:
        print("Error: Tile size too small")
        return 0, 0
    
    return tile_x, tile_y
    
def trim(im, debug = False):
    """ 
    Automatically crops a solid color border off of the image.
    """
    
    #If an image wasn't passed, then don't even try to do anything
    if im is None:
        return None
        
    bg = Image.new(im.mode, im.size, "black")
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if debug:
        print("Original size:")
        print(im.size)
        print("bbox:")
        print(bbox)
    if bbox:
        return im.crop(bbox)
        