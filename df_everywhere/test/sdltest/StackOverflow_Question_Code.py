import os
os.environ["PYSDL2_DLL_PATH"] = os.getcwd()
import sdl2
import win32gui

def get_windows_bytitle(title_text, exact = False):    
    """
    Gets window by title text. [Windows Only]
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

#This will return a handle to an open 'Notepad.exe' window.
window_handle = get_windows_bytitle("Untitled", False)

#Create a window so that the hint below can be set
a = sdl2.SDL_CreateWindow("test window", sdl2.SDL_WINDOWPOS_UNDEFINED,sdl2.SDL_WINDOWPOS_UNDEFINED, 200,200, 0 )
#Set hint as recommended by SDL documentation: https://wiki.libsdl.org/SDL_CreateWindowFrom#Remarks
result = sdl2.SDL_SetHint(sdl2.SDL_HINT_VIDEO_WINDOW_SHARE_PIXEL_FORMAT, hex(id(a)))
print(sdl2.SDL_GetError())

np_window = sdl2.SDL_CreateWindowFrom(window_handle[0])
print(sdl2.SDL_GetError())

np_sur = sdl2.SDL_GetWindowSurface(np_window)
print(sdl2.SDL_GetError())

save_sur = sdl2.SDL_CreateRGBSurface(0,np_sur[0].w,np_sur[0].h,32,0,0,0,0)
print(sdl2.SDL_GetError()) 
r = sdl2.SDL_BlitSurface(np_sur, None, save_sur, None)
print(sdl2.SDL_GetError())

result = sdl2.SDL_SaveBMP(save_sur,'test.bmp')
print(sdl2.SDL_GetError())
sdl2.SDL_FreeSurface(save_sur)
print(sdl2.SDL_GetError())
