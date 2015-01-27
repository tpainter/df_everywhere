
import os
import sys

os.environ["PYSDL2_DLL_PATH"] = os.getcwd()
import sdl2

import win32gui
import win32ui

def get_windows_bytitle(title_text, exact = False):    
    """
    Gets details of window position by title text. [Windows Only]
    """   
    
    
    def _window_callback(hwnd, all_windows):
        all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    windows = []
    win32gui.EnumWindows(_window_callback, windows)
    if exact:
        return [hwnd for hwnd, title in windows if title_text == title]
    else:
        return [hwnd for hwnd, title in windows if title_text in title]





sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) 

'''
a = sdl2.SDL_CreateWindow("test window", sdl2.SDL_WINDOWPOS_UNDEFINED,sdl2.SDL_WINDOWPOS_UNDEFINED, 200,200, 0 )
test_sur = sdl2.SDL_GetWindowSurface(a)
#print test_sur
image = sdl2.SDL_LoadBMP("testimage.bmp")
sdl2.SDL_BlitSurface(image, None, test_sur, None)
sdl2.SDL_FreeSurface(image)
sdl2.SDL_UpdateWindowSurface(a)
'''

#window_handle = get_windows_bytitle("Dwarf Fortress", True) 
window_handle = get_windows_bytitle("Untitled", False)
#window_handle = get_windows_bytitle("test window", True) 
#hwndDC = win32gui.GetWindowDC(window_handle[0])
#mfcDC = win32ui.CreateDCFromHandle(hwndDC)
#print window_handle
#print hwndDC
#print mfcDC

#result = sdl2.SDL_SetHint(sdl2.SDL_HINT_VIDEO_WINDOW_SHARE_PIXEL_FORMAT, hex(id(a)))
#print result
print(sdl2.SDL_GetError()) 

df_window = sdl2.SDL_CreateWindowFrom(window_handle[0])
#df_window = sdl2.SDL_CreateWindowFrom(hwndDC)
#df_window = sdl2.SDL_CreateWindowFrom(mfcDC)
print(sdl2.SDL_GetError())
print sdl2.SDL_GetRenderer(df_window)
#print df_window
#print a
#print hex(id(a))

df_sur = sdl2.SDL_GetWindowSurface(df_window)
print(sdl2.SDL_GetError())

save_sur = sdl2.SDL_CreateRGBSurface(0,df_sur[0].w,df_sur[0].h,32,0,0,0,0)
#print df_sur
#print df_sur[0]
#print df_sur[1]
print(sdl2.SDL_GetError()) 
r = sdl2.SDL_BlitSurface(df_sur, None, save_sur, None)
print(sdl2.SDL_GetError())

#print r
result = sdl2.SDL_SaveBMP(save_sur,'test.bmp')
#result = sdl2.SDL_SaveBMP(df_sur,'test.bmp')
print(sdl2.SDL_GetError()) 
print result
sdl2.SDL_FreeSurface(df_sur)
print(sdl2.SDL_GetError())
exit()