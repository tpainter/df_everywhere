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

'''
This module acts as a singleton.
http://stackoverflow.com/questions/6255050/python-thinking-of-a-module-and-its-variables-as-a-singleton-clean-approach
http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
'''

import sys

from util import getTerminalSize

#These are globals.
_lastUpdate = ''
_systemText = sys.platform

sizex, sizey = getTerminalSize.getTerminalSize()
_consoleWidth = sizex

def console(kind, text):
    """
    Handles whether to print a new line or just overwrite.
    """
    
    if kind == 'log':
        _log(text)
    elif kind == 'update':
        _update(text)
    else:
        return

def _log(text):
    """
    Adds new line to console and puts update text back at bottom.
    """
    global _lastUpdate
    global _consoleWidth
    
    outputString = text
    #This is needed because the apparent console size is different on windows and linux
    if _systemText == 'win32':
        sys.stdout.write("{0:<{1}}\n".format(text, _consoleWidth - 1))
    elif _systemText == "linux" or _systemText == "linux2":
        sys.stdout.write("{0:<{1}}".format(text, _consoleWidth))
    _update(_lastUpdate)
    
def _update(text):
    """
    Overwrites bottom line on console.
    """
    
    global _lastUpdate
    global _consoleWidth
    
    _lastUpdate = text
    #This is needed because the apparent console size is different on windows and linux
    if _systemText == 'win32':
        sys.stdout.write("{0:<{1}}\r".format("Press [q] to exit. "+ text, _consoleWidth - 1))
    elif _systemText == "linux" or _systemText == "linux2":
        sys.stdout.write("{0:<{1}}\r".format("Press [q] to exit. "+ text, _consoleWidth))
    
    #Make sure that text is displayed...
    sys.stdout.flush()
    