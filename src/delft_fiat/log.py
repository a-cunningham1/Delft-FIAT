import atexit
import io
import os
import sys
import threading
import weakref
from datetime import datetime
from enum import Enum

STREAM_COUNT = 1

_Global_and_Destruct_Lock = threading.RLock()
_Loggers = weakref.WeakValueDictionary()


class LogItem:
    def __init__(self, level, msg):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.level = level
        self.msg = msg

    def __str__(self):
        return f"{self.timestamp:20s} {self.level:8s} {self.msg}\n"


def _Destruction():
    items = list(_Loggers.items())
    for key, logger in items:
        logger.Acquire()
        logger.Flush()
        logger.Close()
        logger.Release()


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
        name: str = None,
        stream: type = None,
    ):
        self.Level = _Level(level)

        if stream is None:
            stream = sys.stdout
        self.stream = stream

        if name is None:
            if hasattr(self.stream, "name"):
                self._Name = self.stream.name
            else:
                global STREAM_COUNT
                self._Name = f"Generic_Stream{STREAM_COUNT}"
                STREAM_COUNT += 1
        else:
            self._Name = name

        _Loggers[self._Name] = self

        self._Lock = threading.RLock()

    def Acquire(self):
        self._Lock.acquire()

    def Release(self):
        self._Lock.release()

    def Emit(self, msg):
        self.stream.write(msg)
        self.Flush()

    def Flush(self):
        self.Acquire()
        self.stream.flush()
        self.Release()

    def Close(self):
        _Global_and_Destruct_Lock.acquire()
        self._Closed = True
        del _Loggers[self._Name]
        _Global_and_Destruct_Lock.release()


class FileLogger(StreamLogger):
    def __init__(self, level: int, dst: str, name: str = None):
        if name is None:
            name = "fiat_logging"
        self._filename = os.path.join(dst, f"{name}.log")
        StreamLogger.__init__(self, level, name, self._Open())

    def _Open(self):
        return open(self._filename, "w")

    def Close(self):
        self.Acquire()
        self.Flush()
        stream = self.stream
        self.stream = None
        stream.close()
        StreamLogger.Close()
        self.Release()


class Log:
    def __init__(
        self,
        dst: str,
        name: str = None,
        log_level: int = 2,
        cmd_stream=True,
        cmd_level: int = 2,
    ):
        """_summary_

        Parameters
        ----------
        name : _type_
            _description_
        log_level : int, optional
            _description_, by default 2
        cmd_stream : bool, optional
            _description_, by default True
        cmd_level : int, optional
            _description_, by default 3
        """
        self._loggers = []
        self._loggers.append(FileLogger(level=log_level, dst=dst, name=name))
        if cmd_stream:
            self._loggers.append(StreamLogger(level=cmd_level))

    def __del__(self):
        pass

    def _Log(self, item):
        for logger in self._loggers:
            if LogLevels[item.level].value < logger.Level:
                continue
            else:
                logger.Emit(str(item))

    def HandleLog(log_m):
        def handle(self, *args, **kwargs):
            lvl, msg = log_m(self, *args, **kwargs)
            self._Log(LogItem(level=lvl, msg=msg))

        return handle

    @HandleLog
    def Debug(self, msg: str):
        return "DEBUG", msg

    @HandleLog
    def Info(self, msg: str):
        return "INFO", msg

    @HandleLog
    def Warning(self, msg: str):
        return "WARNING", msg

    @HandleLog
    def Error(self, msg: str):
        return "ERROR", msg

    @HandleLog
    def Dead(self, msg: str):
        return "DEAD", msg


if __name__ == "__main__":
    log = Log("C:\\temp")
    pass
