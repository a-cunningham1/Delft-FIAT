import atexit
import io
import sys
import threading
import weakref
from datetime import datetime
from enum import Enum

_Loggers = weakref.WeakValueDictionary()


def _Destruction():
    pass


atexit.register(_Destruction)


def _Level(level):
    if level not in LogLevels._value2member_map_:
        raise ValueError("")
    return level


class LogLevels(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    DEAD = 5


class StreamLogger:
    def __init__(
        self,
        level: int = 2,
        stream: type = None,
    ):
        self._Level = _Level(level)

        if stream is None:
            stream = sys.stderr
        self.stream = stream

        self._Lock = threading.RLock()

    @staticmethod
    def Formatter(level, msg):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nLevel = LogLevels(level).name

        return

    def _Acquire(self):
        self._Lock.acquire()

    def _Release(self):
        self._Lock.release()

    def Emit(self):
        self._Acquire()

        self._Release()

    def Flush(self):
        self._Acquire()

        self._Release()
        pass

    def Close(self):
        """Placeholder method for now"""
        pass


class FileLogger(StreamLogger):
    def __init__(self, filename: str):
        self._filename = filename
        StreamLogger.__init__(self, self._Open())
        pass

    def _Open(self):
        open(self._filename, "w")

    def Close(self):
        self._Acquire()
        self._Release()


class Log:
    def __init__(
        self,
        name,
        log_level=2,
        stream=True,
        stream_level=3,
    ):
        """_summary_

        Parameters
        ----------
        name : str, optional
            _description_, by default ''
        log_level : int, optional
            _description_, by default 2
        stream : bool, optional
            _description_, by default True
        stream_level : int, optional
            _description_, by default 3
        """
        pass

    def __del__(self):
        pass

    def _Log():
        pass

    def Debug(self, msg: str):
        self._Log()

    def Info(self, msg: str):
        pass

    def Warning(self, msg: str):
        pass

    def Error(self, msg: str):
        pass

    def Dead(self, msg: str):
        pass


if __name__ == "__main__":
    log = Log("FIAT")
    pass
