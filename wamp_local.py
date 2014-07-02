
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from twisted.internet.endpoints import clientFromString
from autobahn.wamp.router import RouterFactory
from autobahn.twisted.wamp import RouterSessionFactory
from autobahn.twisted.wamp import ApplicationSessionFactory
from autobahn.twisted.websocket import WampWebSocketServerFactory
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.websocket import WampWebSocketClientFactory


from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks
      
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
    
    #@inlineCallbacks
    def onJoin(self, details):
        if not self in self.factory._myConnection:
            self.factory._myConnection.append(self)
            
                 

        #yield self.subscribe(sendInput.receiveCommand, 'df_everywhere.g1.commands')
        
        
    def onLeave(self, details):
        if self in self.factory._myConnection:
            self.factory._myConnection.remove(self)
        self.disconnect()

def wampServ(wampAddress, wampPort, wampDebug = False):
    """
    Sets up an Autobahn|Python WAMPv2 server.
    Code modified from WAMP documentation.
    """
    
    ## create a WAMP router factory        
    router_factory = RouterFactory()

    ## create a WAMP router session factory        
    session_factory = RouterSessionFactory(router_factory)

    ## create a WAMP-over-WebSocket transport server factory        
    transport_factory = WampWebSocketServerFactory(session_factory, wampAddress, debug = wampDebug)
    transport_factory.setProtocolOptions(failByDrop = False)

    ## Start websocket server
    server = serverFromString(reactor, wampPort)
    server.listen(transport_factory)
    
def wampClient(wampAddress, wampClientEndpoint):
    """
    Sets up an Autobahn|python WAMPv2 client.
    Code modified from WAMP documentation.
    """
        
    session_factory = ApplicationSessionFactory()
    
    ## .. and set the session class on the factory  
    session_factory._myConnection = []
    session_factory.session = SubpubTileset
    
    ## create a WAMP-over-WebSocket transport client factory    
    #transport_factory = WampWebSocketClientFactory(session_factory, wampAddress, debug = False)
    transport_factory = WampWebSocketClientFactory(session_factory, wampAddress, debug = False, debug_wamp = False)
    transport_factory.setProtocolOptions(failByDrop = False)
    
    ## start a WebSocket client from an endpoint
    client = clientFromString(reactor, wampClientEndpoint)
    client.connect(transport_factory)
    
    return session_factory._myConnection