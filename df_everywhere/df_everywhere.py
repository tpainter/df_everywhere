# DF Everywhere
# Copyright (C) 2014  Travis Painter
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
    
    
if __name__ == "__main__":
    """
    When run directly, it finds Dwarf Fortress window
    """
    import sys
    from sys import platform as _platform
    import time
    import ConfigParser
    from twisted.internet import reactor
    from twisted.internet.defer import inlineCallbacks    
    
    from util import wamp_local, utils, tileset, sendInput, messages, game, consoleInput
    
    #Change this to True for enhanced debugging    
    edebug = False
    if edebug:
        from twisted.python import log
        import sys
        log.startLogging(sys.stdout)    
        
        #Uncomment the two lines below to get more detailed errors
        from twisted.internet.defer import setDebugging
        setDebugging(True)
    
    #Use this for timing the number of cycles per second
    timing = False
    
    
    messages.welcome()
    
    #If 'localTest' file is present, use separate configuration
    import os.path
    localTest = os.path.isfile('localTest')
    if localTest:
        print("localTest file found. Proceeding appropriately.")
    
    Config = ConfigParser.ConfigParser()
    try:
        if localTest:
            Config.read(".\localTest")
        else:
            Config.read(".\dfeverywhere.conf")
        web_topic = Config.get('dfeverywhere', 'TOPIC')
        web_key = Config.get('dfeverywhere', 'KEY')
        try:
            show_fps = Config.getboolean('dfeverywhere', 'FPS')
        except:
            show_fps = False
    except:
        #If file is missing, return blanks
        web_topic = ''
        web_key = ''
    
    if (web_topic == '') or (web_key == ''):
        #No credentials entered, ask for credentials to be entered
        print("No configuration details entered. Please add your credentials to 'dfeverywhere.conf'.")
        raw_input('DF Everywhere stopped. Press [enter] to close this window.')
        sys.exit()
    
            
    #Change screenshot method based on operating system    
    if _platform == "linux" or _platform == "linux2":
        print("Linux unsupported at this time. Exiting...")
        raw_input('DF Everywhere stopped. Press [enter] to close this window.')
        sys.exit()
    elif _platform == "darwin":
        print("OS X unsupported at this time. Exiting...")
        raw_input('DF Everywhere stopped. Press [enter] to close this window.')
        sys.exit()
    elif _platform == "win32":
        # Windows..
        window_handle = utils.get_windows_bytitle("Dwarf Fortress")            
        try:
            shot = utils.screenshot(window_handle[0], debug = False)
        except:
            print("Unable to find Dwarf Fortress window. Ensure that it is running.")
            raw_input('DF Everywhere stopped. Press [enter] to close this window.')
            sys.exit()
    else:
        print("Unsupported platform detected. Exiting...")
        raw_input('DF Everywhere stopped. Press [enter] to close this window.')
        sys.exit()
    
    
    trimmedShot = utils.trim(shot, debug = False)
    tile_x, tile_y = utils.findTileSize(trimmedShot)
    
    #loop through finding a tile size until it is successful
    if (tile_x == 0) or (tile_y == 0):
        while True:
            time.sleep(2)
            shot = utils.screenshot(window_handle[0], debug = False)
            trimmedShot = utils.trim(shot, debug = False)
            if trimmedShot is not None:
                tile_x, tile_y = utils.findTileSize(trimmedShot)
                if (tile_x != 0) or (tile_y != 0):
                    break
    
    
    local_file = utils.findLocalImg(tile_x, tile_y)
    tset = tileset.Tileset(local_file, tile_x, tile_y, array = True, debug = False)
    
    #Start input handler
    inputHandler = consoleInput.ConsoleInput()
    reactor.callWhenRunning(inputHandler.start)
    
    #Start WAMP client
    client_control = game.Game(web_topic, web_key, window_handle[0], fps = show_fps)    
    client_control.tileset = tset
    
    reactor.run()
    