
    
    
if __name__ == "__main__":
    """
    When run directly, it finds Dwarf Fortress window
    """  
    from sys import platform as _platform
    from twisted.internet import reactor
    import utils
    import tileset
    import sendInput
    
    from twisted.internet.defer import inlineCallbacks
    
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)        
    
    import wamp_local
    
    #Uncomment the two lines below to get more detailed errors
    #from twisted.internet.defer import setDebugging
    #setDebugging(True)
    
    #If 'localTest' file is present, use separate configuration
    import os.path
    localTest = os.path.isfile('localTest')
    if localTest:
        print("localTest file found. Proceeding appropriately.")
    
    debug_all = False
    need_wamp_server = False
    
    if need_wamp_server:
        #Start WAMP server
        wamp_local.wampServ("ws://localhost:7081/ws", "tcp:7081", False)
    
        
    #Start WAMP client
    client = wamp_local.WampHolder()
    if need_wamp_server:
        #Connect to local server
        client.connection = wamp_local.wampClient("ws://192.168.0.20:7081/ws", "tcp:192.168.0.20:7081")
    else:
        client.connection = wamp_local.wampClient("ws://dfeverywhere.com:7081/ws", "tcp:dfeverywhere.com:7081")
            
    #Change screenshot method based on operating system    
    if _platform == "linux" or _platform == "linux2":
        print("Linux unsuported at this time. Exiting...")
        exit()
    elif _platform == "darwin":
        print("OS X unsuported at this time. Exiting...")
        exit()
    elif _platform == "win32":
        # Windows..
        window_handle = utils.get_windows_bytitle("Dwarf Fortress")
        shot = utils.screenshot(window_handle[0], debug = False)
    else:
        print("Unsuported platform detected. Exiting...")
        exit()
    
    shot = utils.trim(shot, debug = False)
    #It is possible that shot can be "None". Need to handle this gracefully... Try it another way?
    tile_x, tile_y = utils.findTileSize(shot)
    local_file = utils.findLocalImg(tile_x, tile_y)
    tset = tileset.Tileset(local_file, tile_x, tile_y, debug = False)
    
    localCommands = sendInput.SendInput(window_handle[0])
    
    runContinuously = True
    tickMax = 80
    
    @inlineCallbacks
    def keepGoing(tick):
        
        shot = utils.screenshot(window_handle[0], debug = False)
        trimmedShot = utils.trim(shot, debug = False)
        
        shot_x, shot_y = shot.size
        trimmedShot_x, trimmedShot_y = trimmedShot.size
        
        if (trimmedShot_x != tset.screen_x) or (trimmedShot_y != tset.screen_y):
            print("Error with screen dimensions.")
            #shot.save('screenerror%d.png' % tick)
            #trimmedShot.save('screenerror%da.png' % tick)

        if trimmedShot is not None:
            #Only send a full tile map every 5 ticks, otherwise just send changes
            if (tick + 1) % 20 == 0:
                tileMap = tset.parseImage(trimmedShot, returnFullMap = True)
            else:
                tileMap = tset.parseImage(trimmedShot, returnFullMap = False)
        else:
            #If there was an error getting the tilemap, fake one.
            print("Faking tileMap.")
            tileMap = []
                
        if len(client.connection) > 0 and len(client.subscriptions) < 1:
            #add a subscription once
            if localTest:
                d = yield client.connection[0].subscribe(localCommands.receiveCommand, 'df_everywhere.test.commands')
                d1 = yield client.connection[0].subscribe(client.receiveHeartbeats, 'df_everywhere.test.heartbeats')
            else:
                d = yield client.connection[0].subscribe(localCommands.receiveCommand, 'df_everywhere.g1.commands')                
                d1 = yield client.connection[0].subscribe(client.receiveHeartbeats, 'df_everywhere.g1.heartbeats')
            client.subscriptions.append(d)
            print("WAMP connected...")
            
        if len(client.connection) > 0 and len(client.rpcs) < 1:
            #register a rpc once
            if localTest:
                d = yield client.connection[0].register(tset.wampSend, 'df_everywhere.test.tilesetimage')
            else:
                d = yield client.connection[0].register(tset.wampSend, 'df_everywhere.g1.tilesetimage')
            client.rpcs.append(d)
            
        if len(client.connection) > 0:
            if localTest:
                client.connection[0].publish("df_everywhere.test.map",tileMap)
            else:
                client.connection[0].publish("df_everywhere.g1.map",tileMap)
        else:
            print("Waiting for WAMP connection.")
        
                    
        #Periodically publish the latest tileset filename
        if tick % 10 == 0:
            if len(client.connection) > 0:
                if localTest:
                    client.connection[0].publish("df_everywhere.test.tileset", tset.filename)
                else:
                    client.connection[0].publish("df_everywhere.g1.tileset", tset.filename)
        
        #Periodically publish the screen size and tile size
        if tick % 50 == 1:
            if len(client.connection) > 0:
                if localTest:
                    client.connection[0].publish("df_everywhere.test.screensize", [tset.screen_x, tset.screen_y])
                    client.connection[0].publish("df_everywhere.test.tilesize", [tset.tile_x, tset.tile_y])
                else:
                    client.connection[0].publish("df_everywhere.g1.screensize", [tset.screen_x, tset.screen_y])
                    client.connection[0].publish("df_everywhere.g1.tilesize", [tset.tile_x, tset.tile_y])
        
        #Deal with heartbeats
        if client.heartbeatCounter > 0:
                client.heartbeatCounter -= 1
        if client.heartbeatCounter % 100 == 1:
            print("Heartbeat counter is: %d" % client.heartbeatCounter)
            
        if client.heartbeatCounter < 1:
            #No clients have connected recently, slow processing
            print("No hearbeats recieved, slowing...")            
            reactor.callLater(0.5, keepGoing, tick + 1)
        elif (tick < tickMax or runContinuously):
            reactor.callLater(0.15, keepGoing, tick + 1)
        else:
            print("Tick limit reached. Exiting...")
            reactor.stop()
            
    
    reactor.callLater(0, keepGoing, 0)
    reactor.run()
    