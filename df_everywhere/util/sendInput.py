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

#
# Converts submitted command string to a key command to "type" into a window
#
#


class SendInput:
    """
    Converts received commands (text) and sends them to the window after sanitation.
    """
    
    def __init__(self, hwnd):
        
        #The window that commands are sent to
        self.hwnd = hwnd
        
        #Codes to use with SendKeys
        self._command_SendKeys = { 'a': 'a',
                        'b': 'b',
                        'c': 'c',
                        'd': 'd',
                        'e': 'e',
                        'f': 'f',
                        'g': 'g',
                        'h': 'h',
                        'i': 'i',
                        'j': 'j',
                        'k': 'k',
                        'l': 'l',
                        'm': 'm',
                        'n': 'n',
                        'o': 'o',
                        'p': 'p',
                        'q': 'q',
                        'r': 'r',
                        's': 's',
                        't': 't',
                        'u': 'u',
                        'v': 'v',
                        'w': 'w',
                        'x': 'x',
                        'y': 'y',
                        'z': 'z',
                        'A': '+a',
                        'B': '+b',
                        'C': '+c',
                        'D': '+d',
                        'E': '+e',
                        'F': '+f',
                        'G': '+g',
                        'H': '+h',
                        'I': '+i',
                        'J': '+j',
                        'K': '+k',
                        'L': '+l',
                        'M': '+m',
                        'N': '+n',
                        'O': '+o',
                        'P': '+p',
                        'Q': '+q',
                        'R': '+r',
                        'S': '+s',
                        'T': '+t',
                        'U': '+u',
                        'V': '+v',
                        'W': '+w',
                        'X': '+x',
                        'Y': '+y',
                        'Z': '+z',
                        '0': '0',
                        '1': '1',
                        '2': '2',
                        '3': '3',
                        '4': '4',
                        '5': '5',
                        '6': '6',
                        '7': '7',
                        '8': '8',
                        '9': '9',
                        '!': '!',
                        '"': '"',
                        '#': '#',
                        '$': '$',
                        '%': '%',
                        '&': '&',
                        '\'': '\'',
                        '(': '(',
                        ')': ')',
                        '*': '*',
                        '+': '+',
                        ',': ',',
                        '-': '-',
                        '.': '.',
                        '/': '/',
                        ':': ':',
                        ';': ';',
                        '<': '<',
                        '=': '=',
                        '>': '>',
                        '?': '?',
                        '@': '@',
                        '[': '[',
                        '\\': '\\',
                        ']': ']',
                        '^': '^',
                        '_': '_',
                        '`': '`',
                        '{': '{',
                        '|': '|',
                        '}': '}',
                        '~': '~',
                        'tab': '{TAB}',
                        'enter': '{ENTER}',
                        'esc': '{ESC}',
                        'space': '{SPACE}',
                        'pageup': '{PGUP}',
                        'pagedown': '{PGDN}',
                        'end': '{END}',
                        'home': '{HOME}',
                        'left': '{LEFT}',
                        'up': '{UP}',
                        'right': '{RIGHT}',
                        'down': '{DOWN}',
        }
        
        #Codes to use with pyUserInput
        self._command_pyUserInput = { 'a': 'a',
                        'b': 'b',
                        'c': 'c',
                        'd': 'd',
                        'e': 'e',
                        'f': 'f',
                        'g': 'g',
                        'h': 'h',
                        'i': 'i',
                        'j': 'j',
                        'k': 'k',
                        'l': 'l',
                        'm': 'm',
                        'n': 'n',
                        'o': 'o',
                        'p': 'p',
                        'q': 'q',
                        'r': 'r',
                        's': 's',
                        't': 't',
                        'u': 'u',
                        'v': 'v',
                        'w': 'w',
                        'x': 'x',
                        'y': 'y',
                        'z': 'z',
                        'A': 'A',
                        'B': 'B',
                        'C': 'C',
                        'D': 'D',
                        'E': 'E',
                        'F': 'F',
                        'G': 'G',
                        'H': 'H',
                        'I': 'I',
                        'J': 'J',
                        'K': 'K',
                        'L': 'L',
                        'M': 'M',
                        'N': 'N',
                        'O': 'O',
                        'P': 'P',
                        'Q': 'Q',
                        'R': 'R',
                        'S': 'S',
                        'T': 'T',
                        'U': 'U',
                        'V': 'V',
                        'W': 'W',
                        'X': 'X',
                        'Y': 'Y',
                        'Z': 'Z',
                        '0': '0',
                        '1': '1',
                        '2': '2',
                        '3': '3',
                        '4': '4',
                        '5': '5',
                        '6': '6',
                        '7': '7',
                        '8': '8',
                        '9': '9',
                        '!': '!',
                        '"': '"',
                        '#': '#',
                        '$': '$',
                        '%': '%',
                        '&': '&',
                        '\'': '\'',
                        '(': '(',
                        ')': ')',
                        '*': '*',
                        '+': '+',
                        ',': ',',
                        '-': '-',
                        '.': '.',
                        '/': '/',
                        ':': ':',
                        ';': ';',
                        '<': 'less',
                        '=': '=',
                        '>': '>',
                        '?': '?',
                        '@': '@',
                        '[': '[',
                        '\\': '\\',
                        ']': ']',
                        '^': '^',
                        '_': '_',
                        '`': '`',
                        '{': '{',
                        '|': '|',
                        '}': '}',
                        '~': '~',
                        'tab': 'Tab',
                        'enter': 'Return',
                        'esc': 'Escape',
                        'space': ' ',
                        'pageup': 'Page_Up',
                        'pagedown': 'Page_Down',
                        'end': 'End',
                        'home': 'Home',
                        'left': 'Left',
                        'up': 'Up',
                        'right': 'Right',
                        'down': 'Down',
        }
        
        #Detect whether program is on Windows or Linux
        from sys import platform as _platform
        if _platform == "linux" or _platform == "linux2":
            #linux...
            from pykeyboard import PyKeyboard
            self._sendCommand = self._sendCommandLinux
            self._command = self._command_pyUserInput
            self.k = PyKeyboard()
        elif _platform == "win32":
            # Windows...
            import win32gui
            import SendKeys
            self._sendCommand = self._sendCommandWindows
            self._command = self._command_SendKeys
        else:
            raw_input("Input platform unsupported or unknown: %s" % _platform)
            sys.exit()
        
        
        
    
    def _sanitizeCommand(self, dirtyCommand):
        #return command from dictionary. If it doesn't exist, return 'None'
        return self._command.get(dirtyCommand, None)
    
    def _sendCommandWindows(self, com):
        #This makes the window active and sends keyboard events directly.
        #Windows only.
        #print("Got: %s" % com)
        result = win32gui.SetForegroundWindow(self.hwnd)
        SendKeys.SendKeys(com)   

    def _sendCommandLinux(self, com):
        #This makes the window active and sends keyboard events directly.
        #This is for linux only, but may work for Windows also.
        import gtk.gdk
        if not self.hwnd.is_active():
            now = gtk.gdk.x11_get_server_time(gtk.gdk.get_default_root_window())
            self.hwnd.activate(now)
        self.k.tap_key(com)      
        
    def receiveCommand(self, dirtyCommand):
        """
        Sanitizes command then sends it to window.
        """
        #print("received: %s" % dirtyCommand)
        cleanCommand = self._sanitizeCommand(dirtyCommand)
        #print("cleaned: %s" % cleanCommand)
        if cleanCommand is not None:
            self._sendCommand(cleanCommand)
        