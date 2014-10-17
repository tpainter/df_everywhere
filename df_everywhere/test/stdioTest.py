#from: http://stackoverflow.com/questions/10361820/simple-twisted-echo-client
from twisted.internet.threads import deferToThread as _deferToThread
from twisted.internet import reactor

def mmprint(s):
    pass

class TwistedRAWInput(object):
    def start(self,callable,terminator):
        self.callable=callable
        self.terminator=terminator
        self.startReceiving()
    def startReceiving(self,s=''):
        if s!=self.terminator:
            self.callable(s)
            _deferToThread(raw_input,':').addCallback(self.startReceiving)
        else:
            reactor.stop()


tri = TwistedRAWInput()
reactor.callWhenRunning(tri.start,mmprint,'q')
reactor.callLater(3, mmprint, 'blank')
reactor.callLater(4, mmprint, 'blank1')
reactor.callLater(5, mmprint, 'blank2')
reactor.callLater(6, mmprint, 'blank3')
reactor.run()