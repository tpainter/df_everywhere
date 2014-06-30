


from autobahn.twisted.wamp import ApplicationSession
import sendInput
      
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
            
        #self.subscribe(sendInput.receiveCommand, "df_anywhere.g1.commands")
        def onEvent(event):
            print(event)
        self.subscribe(onEvent, "df_anywhere.g1.commands")
        
    def onLeave(self, details):
        if self in self.factory._myConnection:
            self.factory._myConnection.remove(self)
        self.disconnect()