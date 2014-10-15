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

from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString

from autobahn.twisted.wamp import ApplicationSessionFactory
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.websocket import WampWebSocketClientFactory
from autobahn.wamp import types
from autobahn.wamp import auth


      
class SubpubTileset(ApplicationSession):
    """
    An application component that subscribes and receives events.
    """
    
    def onConnect(self):
        self.join(self.config.realm, [u"wampcra"], self.config.extra['topic'])
    
    def onChallenge(self, challenge):
        #print challenge
        if challenge.method == u"wampcra":
            if u'salt' in challenge.extra:
                key = auth.derive_key(self.config.extra['topic'], challenge.extra['salt'],
                challenge.extra.get('iterations', None), challenge.extra.get('keylen', None))
            else:
                key = self.config.extra['topic']
            signature = auth.compute_wcs(key, challenge.extra['challenge'])
            return signature
        else:
            raise Exception("don't know how to compute challenge for authmethod {}".format(challenge.method))
    
    def onJoin(self, details):
        if not self in self.factory._myConnection:
            self.factory._myConnection.append(self)
            
    def onLeave(self, details):
        if self in self.factory._myConnection:
            self.factory._myConnection.remove(self)
        self.disconnect()
        

def wampServ(wampAddress, wampPort, wampDebug = False):
    """
    Sets up an Autobahn|Python WAMPv2 server.
    Code modified from WAMP documentation.
    """
    from twisted.internet.endpoints import serverFromString
    from autobahn.wamp.router import RouterFactory
    from autobahn.twisted.wamp import RouterSessionFactory
    from autobahn.twisted.websocket import WampWebSocketServerFactory
    
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
    
def wampClient(wampAddress, wampClientEndpoint, topic, key):
    """
    Sets up an Autobahn|python WAMPv2 client.
    Code modified from WAMP documentation.
    """
    
    component_config = types.ComponentConfig(realm = "realm1", extra = {'key': unicode(key), 'topic': unicode(topic)})
    session_factory = ApplicationSessionFactory(config = component_config)  
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