#Tests the round-trip time of the WAMP router. (ping)
import time

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession



class ComponentServer(ApplicationSession):
   """
   An application component that publishes an event every second.
   """

   @inlineCallbacks
   def onJoin(self, details):
      print("session attached")
      while True:
         t = time.time()
         print("Sent time: {}".format(t))
         self.publish('df_everywhere.test.test.time', t)
         yield sleep(1)


if __name__ == '__main__':
   from autobahn.twisted.wamp import ApplicationRunner
   #runner = ApplicationRunner("ws://router1.dfeverywhere.com:7081/ws", "realm1") #0.1 BuyVM
   #runner = ApplicationRunner("ws://192.168.0.20:7081/ws", "realm1") #0.008 local
   #runner = ApplicationRunner("ws://54.68.14.163:7081/ws", "realm1") #0.08 AWS-micro
   runner = ApplicationRunner("ws://23.251.147.152:7081/ws", "realm1") #0.05 google-micro
   runner.run(ComponentServer)