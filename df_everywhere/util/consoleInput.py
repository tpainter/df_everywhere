#from: http://stackoverflow.com/questions/10361820/simple-twisted-echo-client
#and
#from: http://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user
from twisted.internet.threads import deferToThread as _deferToThread
from twisted.internet import reactor


class ConsoleInput(object):

    def __init__(self, stopFunction, reconnectFunction):
        self.stopFunction = stopFunction
        self.reconnectFunction = reconnectFunction
    
    def start(self):
        self.terminator = 'q'
        self.restart = 'r'
        self.getKey = _Getch()
        self.startReceiving()
    def startReceiving(self, s = ''):
        if s == self.terminator:
            self.stopFunction()
        elif s == self.restart:
            self.reconnectFunction()
            _deferToThread(self.getKey).addCallback(self.startReceiving)
        else:
            _deferToThread(self.getKey).addCallback(self.startReceiving)
                


class _Getch:
    """
    Gets a single character from standard input.  Does not echo to the screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()