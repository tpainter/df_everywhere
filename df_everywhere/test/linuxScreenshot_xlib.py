#
# Uses xlib to get window and screenshot.
#
# Does Not Work- Cannont find proper window.

from Xlib import display, X
import Image

DF_name = "gedit"
DF_class = (u'Dwarf_Fortress', u'Dwarf_Fortress')
DF_window = []

disp = display.Display()
win_list = disp.screen().root.query_tree().children
for win in win_list:
    name = win.get_wm_name()
    transient_for = win.get_wm_transient_for()
    attrs = win.get_attributes()
    clas = win.get_wm_class()
    #if attrs.map_state == X.IsViewable:
    if name is not None:
    #print win, transient_for, name, clas, attrs.map_state
        print name
        if name == DF_name:
            DF_window.append(win)


for df in DF_window:
    #print df.get_geometry()
    #print df.get_wm_name()
    #print df.list_properties()
    #print df.get_wm_protocols()
    #print df.get_wm_hints()
    #print df.get_wm_state()
    df.circulate(0)
    
#print disp.screen().root.get_geometry()

exit()

X_pix = 50
Y_pix = 0
W_pix = 200
H_pix = 200
raw = disp.screen().root.get_image(X_pix, Y_pix, W_pix, H_pix, X.ZPixmap, 0xffffffff)
screen_shot = Image.fromstring("RGB", (W_pix, H_pix), raw.data, "raw", "BGRX")
screen_shot.save("screenshot_xlib.png")

