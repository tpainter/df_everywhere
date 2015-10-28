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
    import os.path
    import sys
    from sys import platform as _platform
    import time
    import ConfigParser
    
    from twisted.internet import reactor
    from twisted.internet.defer import inlineCallbacks    
    
    from util import wamp_local, utils, tileset, sendInput, messages, game, consoleInput, screenshot
    
    #Change this to True for enhanced debugging    
    edebug = False
    if edebug:
        from twisted.python import log
        import sys
        log.startLogging(sys.stdout)    
        
        #Uncomment the two lines below to get more detailed errors
        from twisted.internet.defer import setDebugging
        setDebugging(True)
    
    
    messages.welcome()
    
    #If 'localTest' file is present, use separate configuration    
    localTest = os.path.isfile('localTest')
    if localTest:
        print("localTest file found. Proceeding appropriately.")
    
    Config = ConfigParser.ConfigParser()
    try:
        if localTest:
            Config.read("localTest")
        else:
            Config.read("dfeverywhere.conf")
        web_topic = Config.get('dfeverywhere', 'TOPIC')
        web_key = Config.get('dfeverywhere', 'KEY')
        
        #Check optional values
        try:
            show_fps = Config.getboolean('dfeverywhere', 'FPS')
        except:
            show_fps = True
        try:
            full_debug = Config.getboolean('dfeverywhere', 'DEBUG')
        except:
            full_debug = False
    except:
        #If file is missing, return blanks
        web_topic = ''
        web_key = ''
    
    if (web_topic == '') or (web_key == ''):
        #No credentials entered, ask for credentials to be entered
        print("No configuration details entered. Please add your credentials to 'dfeverywhere.conf'.")
        raw_input('DF Everywhere stopped. Press [enter] to close this window.')
        sys.exit()
    
    screen_shot = screenshot.ScreenShot("Dwarf Fortress")
    shot = screen_shot.get_screen_shot()
    
    try:
        print("Full image size: %d, %d" % shot.size)
        if full_debug:
            print("Saving initial window image to debug1.png...")
            shot.save("debug1.png")
        trimmedShot = utils.trim(shot, debug = False)
        if full_debug:
            print("Saving trimmed window image to debug2.png...")
            trimmedShot.save("debug2.png")
        tile_x, tile_y = utils.findTileSize(trimmedShot)
    except Exception, e:
        print e
        print("Error getting screenshot. Exiting.")
        sys.exit()
    
    #loop through finding a tile size until it is successful
    if (tile_x == 0) or (tile_y == 0):
        i = 0
        while True:
            i+= 1
            shot = screen_shot.get_screen_shot()
            trimmedShot = utils.trim(shot, debug = False)
            if trimmedShot is not None:
                tile_x, tile_y = utils.findTileSize(trimmedShot)
                if (tile_x != 0) or (tile_y != 0):
                    break
            
            if i > 30:
                #End program after about 60 seconds
                sys.exit(0)
                
            time.sleep(2)
    
    
    local_file = utils.findLocalImg(tile_x, tile_y)
    tset = tileset.Tileset(local_file, tile_x, tile_y, array = True, debug = False)
    
    #Start WAMP client
    client_control = game.Game(web_topic, web_key, screen_shot.get_screen_shot, screen_shot.window_handle, fps = show_fps)    
    client_control.tileset = tset
    
    #Start input handler
    inputHandler = consoleInput.ConsoleInput(client_control.stopClean, client_control.reconnect)
    reactor.callWhenRunning(inputHandler.start)
    
    reactor.run()
    