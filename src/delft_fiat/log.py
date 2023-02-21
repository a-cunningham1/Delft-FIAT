import io
import sys
import threading
from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum

class LogLevels(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    DEAD = 5 

class BaseHandler(metaclass=ABCMeta):

    @abstractmethod    
    def close(self):
        pass

    def filter():
        pass
    pass

class StreamHandler:
    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stderr
        self.stream = stream
        pass

    def Emit():
        pass

    def Flush():
        pass    

    def Close():
        pass

class FileHandler(StreamHandler):
    def __init__(self, filename):
        self._filename = filename
        StreamHandler.__init__(self, self._open())
        pass

    def _open(self):
        open(self._filename, "w")
    
class Log:
    def __init__(
            self,
            name='',
            log_level=2,
            stream=True,
            stream_level=3,
        ):
        pass

    def __del__(self):
        pass

    def _Log():
        pass

    def Debug(self, msg):
        pass
    
    def Info(self, msg):
        pass

    def Warning(self, msg):
        pass

    def Error(self, msg):
        pass

    def Dead(self, msg):
        pass
    
if __name__ == '__main__':
    log = Log()
    pass
