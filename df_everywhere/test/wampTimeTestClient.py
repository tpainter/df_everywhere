#Tests the round-trip time of the WAMP router. (ping)
#Both client and server are meant to be run on same maching.
import time

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession



class ComponentClient(ApplicationSession):
   """
   An application component that subscribes and receives events,
   and stop after having received 5 events.
   """

   @inlineCallbacks
   def onJoin(self, details):
      print("session attached")

      self.received = 0

      def on_event(i):
         t = time.time()
         dif = t - i
         print("Got time: {} at {}. Difference: {}".format(i,t,dif))
         self.received += 1
         if self.received > 5:
            self.leave()

      yield self.subscribe(on_event, 'df_everywhere.test.test.time')


   def onDisconnect(self):
      print("disconnected")
      reactor.stop()




if __name__ == '__main__':
   from autobahn.twisted.wamp import ApplicationRunner
   runner = ApplicationRunner("ws://router1.dfeverywhere.com:7081/ws", "realm1")
   runner.run(ComponentClient)