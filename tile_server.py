


    

        




    


from autobahn.twisted.wamp import ApplicationSession        
class SubpubTileset(ApplicationSession):
    """
    An application component that subscribes and receives events.
    """
    
    def __init__(self, realm = 'realm1'):
        ApplicationSession.__init__(self)
        #This was needed for it to work on one computer... but not others? Strange.
        self._realm = 'realm1'
        
    def onConnect(self):
        self.join(self._realm)
        
    def onJoin(self, details):
        if not self in self.factory._myConnection:
            self.factory._myConnection.append(self)
        
    def onLeave(self, details):
        if self in self.factory._myConnection:
            self.factory._myConnection.remove(self)
        self.disconnect()
    
    
if __name__ == "__main__":
    """
    When run directly, it finds Dwarf Fortress window
    """  
    
    import utils
    from tileset import Tileset
    
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)

    #a fake class to create empty objects
    class expando(object): pass
    client_self = expando()
    #client_self.wamp = []
    from time import sleep
    
    from twisted.internet import reactor
    from twisted.internet.endpoints import serverFromString
    
    ## create a WAMP router factory
    from autobahn.wamp.router import RouterFactory
    router_factory = RouterFactory()

    ## create a WAMP router session factory
    from autobahn.twisted.wamp import RouterSessionFactory
    session_factory = RouterSessionFactory(router_factory)

    ## create a WAMP-over-WebSocket transport server factory
    from autobahn.twisted.websocket import WampWebSocketServerFactory
    transport_factory = WampWebSocketServerFactory(session_factory, "ws://localhost:7081/ws", debug = False)
    transport_factory.setProtocolOptions(failByDrop = False)

    ## Start websocket server
    server = serverFromString(reactor, "tcp:7081")
    server.listen(transport_factory)
    
    ## Set up webserver to tileset image
    from twisted.web.static import File
    resource = File('./')
    from twisted.web.server import Site
    site = Site(resource)
    reactor.listenTCP(7080, site)
    
    #Start WAMP client
    from twisted.internet.endpoints import clientFromString
    
    ## create a WAMP application session factory
    from autobahn.twisted.wamp import ApplicationSessionFactory
    session_factory = ApplicationSessionFactory()
    
    ## .. and set the session class on the factory
    session_factory._myConnection = []
    session_factory.session = SubpubTileset
    
    ## create a WAMP-over-WebSocket transport client factory
    from autobahn.twisted.websocket import WampWebSocketClientFactory
    transport_factory = WampWebSocketClientFactory(session_factory, "ws://127.0.0.1:7081/ws", debug = False, debug_wamp = False)
    transport_factory.setProtocolOptions(failByDrop = False)
    
    ## start a WebSocket client from an endpoint
    client = clientFromString(reactor, "tcp:127.0.0.1:7081")
    client.connect(transport_factory)
    
    #self.wamp = session_factory._myConnection
    client_self.wamp = session_factory._myConnection
    #client_self.wamp.append(session_factory._myConnection)
    
    #wait for a while to make sure that the WAMP connection is running, then add subscription
    #reactor.callLater(5, self.subscribe_heartbeats, "cb.map." + mainconfig.env_control + ".heartbeats")
    
    
    #Change screenshot method based on operating system
    from sys import platform as _platform
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
    tile_x, tile_y = utils.findTileSize(shot)
    local_file = utils.findLocalImg(tile_x, tile_y)
    tset = Tileset(local_file, tile_x, tile_y, debug = False)
        
    tickMax = 40
    
    def keepGoing(tick):
        shot = utils.screenshot(window_handle[0], debug = False)
        shot = utils.trim(shot, debug = False)
        tileMap = tset.parseImage(shot)
        print("tileMap created.")
        if len(client_self.wamp) > 0:
            client_self.wamp[0].publish("df_anywhere.g1.map",tileMap)
            print("Published tilemap.")
        else:
            print("Waiting for WAMP connection.")
            
        #Periodically publish the latest tileset filename
        if tick % 5 == 0:
            if len(client_self.wamp) > 0:
                client_self.wamp[0].publish("df_anywhere.g1.tileset", tset.filename)
                print("Published tileset.")
        
        #Periodically publish the screen size
        if tick % 5 == 1:
            if len(client_self.wamp) > 0:
                client_self.wamp[0].publish("df_anywhere.g1.screensize", (tset.screen_x, tset.screen_y))
                print("Published tileset.")
        
        
        
        if (tick < tickMax):
            reactor.callLater(.2, keepGoing, tick + 1)
        else:
            reactor.stop()
        
    reactor.callWhenRunning(keepGoing, 0)
    reactor.run()
    