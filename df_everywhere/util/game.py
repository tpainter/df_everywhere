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
# 
#
from twisted.internet import reactor, threads
from twisted.internet.defer import inlineCallbacks   

from util import wamp_local, sendInput, utils, prettyConsole

class Game():
    """
    Object to hold all program states and connections.
    """
    
    def __init__(self, web_topic, web_key, window_hnd, fps = False):
        ### FPS reports
        self.fps = fps
        self.fps_counter = 0
        
        ### Tileset
        self.tileset = None
        
        ### Commands
        self.window_hnd = window_hnd
        self.controlWindow = sendInput.SendInput(self.window_hnd)
        
        ### Timing delays
        self.screenDelay = 0.0
        self.filenameDelay = 5
        self.sizeDelay = 5
        self.heartbeatDelay = 1
        self.screenCycles = 0
        
        ### WAMP details
        self.topicPrefix = "df_everywhere.%s" % web_topic
        self.connected = False
        self.connection = None
        self.subscriptions = {}
        self.rpcs = []
        
        ### Heartbeats
        self.heartbeatCounter = 120
        self.slowed = False
        
        ### Connect to WAMP router
        self.connection = wamp_local.wampClient("ws://router1.dfeverywhere.com:7081/ws", "tcp:router1.dfeverywhere.com:7081", web_topic, web_key)
        
        ### Wait for WAMP connection before initializing loops in reactor
        reactor.callLater(0, self._waitForConnection)
        
            
    def _waitForConnection(self):
        """
        Handles waiting for WAMP connection before continuing loading program.
        """
        if self.connection is None:
            prettyConsole.console('log', "Waiting for connection...")
            #Wait and test again
            reactor.callLater(0.5, self._waitForConnection)
        else:
            try:
                a = self.connection[0]
            except:
                prettyConsole.console('log', "Still waiting for connection...")
                #Wait and test again
                reactor.callLater(0.5, self._waitForConnection)
            else:
                prettyConsole.console('log', "Connected...")
                self.connected = True
                reactor.callLater(0, self._registerRPC)
                reactor.callLater(0, self._subscribeCommands)
                reactor.callLater(0, self._subscribeHeartbeats)
                
                ### Initialize reactor loops
                reactor.callLater(self.screenDelay, self._loopScreen)
                reactor.callLater(self.filenameDelay, self._loopFilename)
                reactor.callLater(self.sizeDelay, self._loopTileSize)
                reactor.callLater(self.sizeDelay, self._loopScreenSize)
                reactor.callLater(self.heartbeatDelay, self._loopHeartbeat)
                if self.fps:
                    reactor.callLater(5, self._loopPrintFps)
            
    @inlineCallbacks
    def _registerRPC(self):
        """
        Registers function for remote procedure calls.
        """
        d = yield self.connection[0].register(self.tileset.wampSend, '%s.tilesetimage' % self.topicPrefix)
        self.rpcs.append(d)
    
    @inlineCallbacks
    def _subscribeCommands(self):
        """
        Subscribes to incomming commands.
        """
        d = yield self.connection[0].subscribe(self.controlWindow.receiveCommand, '%s.commands' % self.topicPrefix)
        self.subscriptions['commands'] = d
    
    @inlineCallbacks
    def _subscribeHeartbeats(self):
        """
        Subscribes to incomming heartbeats.
        """
        d = yield self.connection[0].subscribe(self._receiveHeartbeats, '%s.heartbeats' % self.topicPrefix)
        self.subscriptions['heartbeats'] = d
        
    def _receiveHeartbeats(self, recv):
        """
        Tracks heartbeats from clients. Ignore 'recv'.
        """
        #On hearbeat, reset counter.
        self.heartbeatCounter = 120
        if self.slowed:
            prettyConsole.console('log', "Viewer connected. Resuming...")
            self.slowed = False
            
    def _loopHeartbeat(self):
        """
        Handles periodically decreasing heartbeat timer.
        """
        if self.heartbeatCounter > 0:
            self.heartbeatCounter -= 1
            
        if self.heartbeatCounter < 1:
            if not self.slowed:
                prettyConsole.console('log', "No viewers connected, slowing...")
            self.slowed = True
        else:
            self.slowed = False            
        
        reactor.callLater(self.heartbeatDelay, self._loopHeartbeat)
        
    #@inlineCallbacks
    def _loopScreen(self):
        """
        Handles periodically running screen grabs.
        """
        try:
            shot = utils.screenshot(self.window_hnd, debug = False)
            #Need to check that an image was returned.
            shot_x, shot_y = shot.size
        except:
            print("Error getting image. Exiting.")
            reactor.stop()
        
        trimmedShot = utils.trim(shot, debug = False) 
        
        if trimmedShot is not None:
            
            #Only send a full tile map every 20 cycles, otherwise just send changes
            #This is slower with deferToThread
            if (self.screenCycles) % 20 == 0:
                tileMap = self.tileset.parseImageArray(trimmedShot, returnFullMap = True)
                #tileMap = yield threads.deferToThread(self.tileset.parseImageArray, trimmedShot, returnFullMap = True)
            else:
                tileMap = self.tileset.parseImageArray(trimmedShot, returnFullMap = False)
                #tileMap = yield threads.deferToThread(self.tileset.parseImageArray, trimmedShot, returnFullMap = False)
        else:
            #If there was an error getting the tilemap, fake one.
            prettyConsole.console('log', "Image error. Try moving Dwarf Fortress window to main display.")
            tileMap = []
        
        self._sendTileMap(tileMap)
        self.screenCycles += 1
        
        if self.fps:
            self.fps_counter += 1
        
        reactor.callLater(self.screenDelay, self._loopScreen)
        
    def _loopFilename(self):
        """
        Handles periodically sending the current tileset filename.
        """
        if self.connected:
            if self.tileset.filename is not None:
                self.connection[0].publish("%s.tileset" % self.topicPrefix, self.tileset.filename)
        
        reactor.callLater(self.filenameDelay, self._loopFilename)
        
    def _loopTileSize(self):
        """
        Handles periodically sending the current tile dimensions.
        """
        if self.connected:
            if (self.tileset.tile_x is not None) and (self.tileset.tile_y is not None):
                self.connection[0].publish("%s.tilesize" % self.topicPrefix, [self.tileset.tile_x, self.tileset.tile_y])
                
        reactor.callLater(self.sizeDelay, self._loopTileSize)
        
    def _loopScreenSize(self):
        """
        Handles periodically sending the current screen dimensions.
        """
        if self.connected:
            if (self.tileset.screen_x is not None) and (self.tileset.screen_y is not None):
                #Only send screen size update if it makes sense
                if (self.tileset.screen_x % self.tileset.tile_x == 0) and (self.tileset.screen_y % self.tileset.tile_y == 0):
                    self.connection[0].publish("%s.screensize" % self.topicPrefix, [self.tileset.screen_x, self.tileset.screen_y])
        
        reactor.callLater(self.sizeDelay, self._loopScreenSize)
        
    def _sendTileMap(self, tilemap):
        """
        Sends tilemap over connection.
        """
        if self.connected:
            if tilemap != []:
                self.connection[0].publish("%s.map" % self.topicPrefix, tilemap)
                
    def _loopPrintFps(self):
        """
        Print number of screen grabs per second.
        """
        prettyConsole.console('update', "FPS: %0.1f" % (self.fps_counter/5.0))
        self.fps_counter = 0
        
        if self.fps:
            reactor.callLater(5, self._loopPrintFps)
            
    def stopClean(self):
        """
        Cleanly stop connection and shutdown.
        """
        self.connected = False
        self.connection[0].disconnect()
        reactor.callLater(2, reactor.stop)
        