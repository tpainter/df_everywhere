#
# Testing windows error raised on exit 
#

import sys
from twisted.internet import reactor
import time

def continuous():
    print(".")
    reactor.callLater(0.5, continuous)
    
    
reactor.callLater(0, continuous)
reactor.callLater(10, reactor.stop)
reactor.run()
sys.exit()