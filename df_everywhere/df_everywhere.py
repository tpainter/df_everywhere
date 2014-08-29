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
    import ConfigParser
    from twisted.internet import reactor
    from twisted.internet.defer import inlineCallbacks    
    
    from util import wamp_local, utils, tileset, sendInput, messages
    
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
    timing = True
    if timing:
        global timedCalls
        timedCalls = 0
    
    
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
        need_wamp_server = False
        topicPrefix = "df_everywhere.%s" % web_topic
    except:
        #If file is missing, start local server
        web_topic = ''
        web_key = ''
        need_wamp_server = True
    
    if (web_topic == '') and (web_key == ''):
        #No credentials entered, ask for credentials to be entered
        print("No configuration details entered. Please add your credentials to 'dfeverywhere.conf'.")
        raw_input('DF Everywhere stopped. Press [enter] to close this window.')
        sys.exit()
        
    if need_wamp_server:
        #Start WAMP server
        wamp_local.wampServ("ws://localhost:7081/ws", "tcp:7081", False)
    
    #Start WAMP client
    client = wamp_local.WampHolder()
    if need_wamp_server:
        #Connect to local server
        client.connection = wamp_local.wampClient("ws://192.168.0.20:7081/ws", "tcp:192.168.0.20:7081")
    else:
        client.connection = wamp_local.wampClient("ws://router1.dfeverywhere.com:7081/ws", "tcp:router1.dfeverywhere.com:7081", web_topic, web_key)
            
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
    local_file = utils.findLocalImg(tile_x, tile_y)
    tset = tileset.Tileset(local_file, tile_x, tile_y, array = True, debug = False)
    
    localCommands = sendInput.SendInput(window_handle[0])
        
    @inlineCallbacks
    def keepGoing(tick):
        try:
            shot = utils.screenshot(window_handle[0], debug = False)
            shot_x, shot_y = shot.size
        except:
            print("Error getting screen shot. Exiting.")
            shot = None
            reactor.stop()
        
        trimmedShot = utils.trim(shot, debug = False)       
        
        if trimmedShot is not None:
            trimmedShot_x, trimmedShot_y = trimmedShot.size
            if (trimmedShot_x != tset.screen_x) or (trimmedShot_y != tset.screen_y):
                #print("Error with screen dimensions.")
                #shot.save('screenerror%d.png' % tick)
                #trimmedShot.save('screenerror%da.png' % tick)
                pass
                
            #Only send a full tile map every 20 ticks, otherwise just send changes
            if (tick + 1) % 20 == 0:
                tileMap = tset.parseImageArray(trimmedShot, returnFullMap = True)
            else:
                tileMap = tset.parseImageArray(trimmedShot, returnFullMap = False)
        else:
            #If there was an error getting the tilemap, fake one.
            print("Faking tileMap.")
            tileMap = []
                
        if len(client.connection) > 0 and len(client.subscriptions) < 1:
            #add a subscription once
            d = yield client.connection[0].subscribe(localCommands.receiveCommand, '%s.commands' % topicPrefix)
            d1 = yield client.connection[0].subscribe(client.receiveHeartbeats, '%s.heartbeats' % topicPrefix)
            
            client.subscriptions.append(d)
            print("WAMP connected...")
            
        if len(client.connection) > 0 and len(client.rpcs) < 1:
            #register a rpc once
            d = yield client.connection[0].register(tset.wampSend, '%s.tilesetimage' % topicPrefix)
            
            client.rpcs.append(d)
            
        if len(client.connection) > 0:
            client.connection[0].publish("%s.map" % topicPrefix,tileMap)
            
        else:
            print("Waiting for WAMP connection.")
        
                    
        #Periodically publish the latest tileset filename
        if tick % 10 == 0:
            if len(client.connection) > 0:
                client.connection[0].publish("%s.tileset" % topicPrefix, tset.filename)
                
        
        #Periodically publish the screen size and tile size
        if tick % 50 == 1:
            if len(client.connection) > 0:
                client.connection[0].publish("%s.tilesize" % topicPrefix, [tset.tile_x, tset.tile_y])
                #Only send screen size update if it makes sense
                if (tset.screen_x % tset.tile_x == 0) and (tset.screen_y % tset.tile_y == 0):
                    client.connection[0].publish("%s.screensize" % topicPrefix, [tset.screen_x, tset.screen_y])
        
        #Deal with heartbeats
        if client.heartbeatCounter > 0:
                client.heartbeatCounter -= 1
                
                if timing:
                    global timedCalls
                    timedCalls += 1
                
                reactor.callLater(0, keepGoing, tick + 1)            
        else:
            #No clients have connected recently, slow processing
            if not client.slowed:
                print("No hearbeats received, slowing...")
                client.slowed = True
            reactor.callLater(0.5, keepGoing, tick + 1)
    
    if timing:
        def timeLoop():
            global timedCalls
            print('Calls per 5 seconds: %d' % timedCalls)
            
            timedCalls = 0
            reactor.callLater(5, timeLoop)
    
    if timing:
        reactor.callLater(5, timeLoop)
    
    reactor.callLater(0, keepGoing, 0)
    reactor.run()
    