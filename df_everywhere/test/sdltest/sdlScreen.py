
import os
import sys

os.environ["PYSDL2_DLL_PATH"] = os.getcwd()
import sdl2

import win32gui

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

window_handle = get_windows_bytitle("Dwarf Fortress", True) 
#window_handle = get_windows_bytitle("Untitled", False) 

df_window = sdl2.SDL_CreateWindowFrom(window_handle[0])
df_sur = sdl2.SDL_GetWindowSurface(df_window)
save_sur = sdl2.SDL_CreateRGBSurface(0,df_sur[0].w,df_sur[0].h,32,0,0,0,0)
result = sdl2.SDL_SaveBMP(save_sur,'test.bmp')
sdl2.SDL_FreeSurface(df_sur)
print(sdl2.SDL_GetError()) 

sys.exit()
