import atexit
import io
import os
import queue
import re
import sys
import threading
import time
import traceback
import weakref
from datetime import datetime
from enum import Enum
from string import Formatter as StrFormatter
from warnings import warn

DEFAULT_FMT = "{asctime:20s}{levelname:8s}{message}"
DEFAULT_TIME_FMT = "%Y-%m-%d %H:%M:%S"
STREAM_COUNT = 1

_Global_and_Destruct_Lock = threading.RLock()
_streams = weakref.WeakValueDictionary()
_loggers = weakref.WeakValueDictionary()

_str_formatter = StrFormatter()
del StrFormatter


def _Destruction():
    """Method called when python exits to clean up"""

    items = list(_streams.items())
    for _, stream in items:
        stream.acquire()
        stream.flush()
        stream.close()
        stream.release()


atexit.register(_Destruction)


def _Level(level):
    """Check if level can be used"""

    if level not in LogLevels._value2member_map_:
        raise ValueError("")
    return level


class LogLevels(Enum):
    """Dumb c-like thing"""

    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    DEAD = 5


class LogItem:
    def __init__(
        self,
        level: str,
        msg: str,
    ):
        """Struct for logging messages..."""

        self.ct = time.time()
        self.level = level
        self.levelname = LogLevels(level).name
        self.msg = msg

    def get_message(
        self,
    ):
        return str(self.msg)


class FormatStyler:
    default_format = "{message}"
    asctime_format = "{asctime}"
    asctime_search = "{asctime"

    fmt_spec = re.compile(
        r"^(.?[<>=^])?[+ -]?#?0?(\d+|{\w+})?[,_]?(\.(\d+|{\w+}))?[bcdefgnosx%]?$", re.I
    )
    field_spec = re.compile(r"^(\d+|\w+)(\.\w+|\[[^]]+\])*$")

    def __init__(self, fmt, *, defaults=None):
        self._fmt = fmt or self.default_format
        self._defaults = defaults

    def uses_time(self):
        return self._fmt.find(self.asctime_search) >= 0

    def validate(self):
        """Validate the input format, ensure it is the correct string formatting style"""
        fields = set()
        try:
            for _, fieldname, spec, conversion in _str_formatter.parse(self._fmt):
                if fieldname:
                    if not self.field_spec.match(fieldname):
                        raise ValueError(
                            "invalid field name/expression: %r" % fieldname
                        )
                    fields.add(fieldname)
                if conversion and conversion not in "rsa":
                    raise ValueError("invalid conversion: %r" % conversion)
                if spec and not self.fmt_spec.match(spec):
                    raise ValueError("bad specifier: %r" % spec)
        except ValueError as e:
            raise ValueError("invalid format: %s" % e)
        if not fields:
            raise ValueError("invalid format: no fields")

    def _format(self, record):
        if defaults := self._defaults:
            values = defaults | record.__dict__
        else:
            values = record.__dict__
        return self._fmt.format(**values)

    def format(self, record):
        try:
            return self._format(record)
        except KeyError as e:
            raise ValueError("Formatting field not found in record: %s" % e)


class MessageFormatter(object):
    """_summary_"""

    _conv = time.localtime

    def __init__(self, fmt=None, datefmt=None, validate=True, *, defaults=None):
        """_summary_"""

        self._style = FormatStyler(fmt, defaults=defaults)
        if validate:
            self._style.validate()

        self._fmt = self._style._fmt
        self.datefmt = datefmt

    def format_time(self, record):
        """_summary_"""

        ct = self._conv(record.ct)
        if datefmt := self.datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime(DEFAULT_TIME_FMT, ct)
        return s

    def format_exception(self, ei):
        """_summary_"""

        sio = io.StringIO()
        tb = ei[2]
        traceback.print_exception(ei[0], ei[1], tb, None, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == "\n":
            s = s[:-1]
        return s

    def uses_time(self):
        """
        Check if the format uses the creation time of the record.
        """
        return self._style.uses_time()

    def format_message(self, record):
        return self._style.format(record)

    def format(self, record):
        """_summary_"""

        record.message = record.get_message()
        if self.uses_time():
            record.asctime = self.format_time(record)
        s = self.format_message(record)
        if s[-1:] != "\n":
            s = s + "\n"
        # if record.exc_info:
        #     # Cache the traceback text to avoid converting it multiple times
        #     # (it's constant anyway)
        #     if not record.exc_text:
        #         record.exc_text = self.format_exception(record.exc_info)
        # if record.exc_text:
        #     if s[-1:] != "\n":
        #         s = s + "\n"
        #     s = s + record.exc_text
        return s


_default_formatter = MessageFormatter(DEFAULT_FMT, DEFAULT_TIME_FMT)


class BaseHandler:
    def __init__(
        self,
        level: int = 2,
    ):
        """Base class for all stream handlers"""

        self.level = _Level(level)
        self.msg_formatter = None
        self._name = None
        self._closed = False

        self._make_lock()

    def __repr__(self):
        pass

    def _add_global_stream_ref(
        self,
    ):
        """_summary_"""

        _Global_and_Destruct_Lock.acquire()
        _streams[self._name] = self
        _Global_and_Destruct_Lock.acquire()

    def _make_lock(self):
        self._lock = threading.RLock()

    def acquire(self):
        self._lock.acquire()

    def release(self):
        self._lock.release()

    def close(self):
        """Close and clean up"""

        _Global_and_Destruct_Lock.acquire()
        self._closed = True
        del _streams[self._name]
        _Global_and_Destruct_Lock.release()

    def emit(self):
        NotImplementedError()

    def flush(self):
        NotImplementedError()

    def format(
        self,
        record: LogItem,
    ):
        """_summary_"""

        if self.msg_formatter:
            msg_fmt = self.msg_formatter
        else:
            msg_fmt = _default_formatter
        return msg_fmt.format(record)

    def set_formatter(
        self,
        formatter: MessageFormatter,
    ):
        """_summary_"""

        self.msg_formatter = formatter


class Sender(BaseHandler):
    def __init__(self, queue):
        """_summary_"""

        BaseHandler.__init__(self)
        self.q = queue

    def put(self, record):
        """_summary_"""

        self.q.put_nowait(record)

    def emit(self, record):
        """Emit a record."""

        try:
            self.put(record)
        except Exception:
            self.handleError(record)


class CHandler(BaseHandler):
    def __init__(
        self,
        level: int = 2,
        stream: type = None,
        name: str = None,
    ):
        """Output text to the console

        Parameters
        ----------
        level : int, optional
            _description_, by default 2
        name : str, optional
            _description_, by default None
        stream : type, optional
            _description_, by default None
        """

        BaseHandler.__init__(self, level=level)

        if stream is None:
            stream = sys.stdout
        self.stream = stream

        if name is None:
            if hasattr(self.stream, "name"):
                self._name = self.stream.name
            else:
                global STREAM_COUNT
                self._name = f"Stream{STREAM_COUNT}"
                STREAM_COUNT += 1
        else:
            self._name = name

        self._add_global_stream_ref()

    def emit(self, record):
        """Emit a certain message"""

        msg = self.format(record)
        self.stream.write(msg)
        self.flush()

    def flush(self):
        """Dump cache to desired destination"""

        self.acquire()
        self.stream.flush()
        self.release()


class FileHandler(CHandler):
    def __init__(
        self,
        level: int,
        dst: str,
        name: str = None,
        mode: str = "w",
    ):
        """Output text to a file

        Parameters
        ----------
        level : int
            _description_
        dst : str
            _description_
        name : str, optional
            _description_, by default None
        """

        if name is None:
            name = "log_default"
        self._filename = os.path.join(dst, f"{name}.log")
        CHandler.__init__(self, level, self._open(mode), name)

    def _open(
        self,
        mode: str = "w",
    ):
        """Open a txt file and return the handler"""

        return open(self._filename, mode)

    def close(self):
        """Close and clean up"""

        self.acquire()
        self.flush()

        stream = self.stream
        self.stream = None

        stream.close()
        CHandler.close(self)
        self.release()


class DummyLog:
    def __init__(
        self,
        obj,
    ):
        """Dummy class for tracking children
        (actually funny..)
        """

        self.child_tree = {obj: None}

    def __repr__(self):
        _mem_loc = f"{id(self):#018x}".upper()
        return f"<{self.__class__.__name__} object at {_mem_loc}>"

    def _check_succession(
        self,
        obj,
    ):
        """Remove child if older one is present"""

        _disinherit = [
            child for child in self.child_tree if child.name.startswith(obj.name)
        ]

        for child in _disinherit:
            del self.child_tree[child]

    def add_to_chain(self, obj):
        """_summary_"""

        self._check_succession(obj)
        self.child_tree[obj] = None


class LogManager:
    def __init__(
        self,
        stuff=None,
    ):
        """_summary_"""

        self.logger_tree = {}

    def _check_children(
        self,
        obj: DummyLog,
        logger: "Log",
    ):
        """Ensure the hierarchy is corrected downwards"""

        name = logger.name

        for child in obj.child_tree.keys():
            if child.parent is None:
                child.parent = logger
            elif not child.parent.name.startswith(name):
                if logger.parent is not child.parent:
                    logger.parent = child.parent
                child.parent = logger

    def _check_parents(self, logger: "Log"):
        """Ensure the hierarchy is corrected upwards"""

        name = logger.name
        parent = None
        parts = name.split(".")

        if len(parts) == 1:
            return
        _l = len(parts) - 1

        for idx in range(_l):
            sub = parts[0 : _l - idx]
            substr = ".".join(sub)

            if substr not in self.logger_tree:
                self.logger_tree[substr] = DummyLog(logger)
            else:
                obj = self.logger_tree[substr]
                if isinstance(obj, Log):
                    parent = obj
                    break
                else:
                    obj.add_to_chain(logger)

        logger.parent = parent
        if parent is not None:
            logger.log_level = parent.log_level

    def resolve_logger_tree(
        self,
        logger: "Log",
    ):
        """_summary_"""

        obj = None
        name = logger.name

        _Global_and_Destruct_Lock.acquire()
        if name in self.logger_tree:
            obj = self.logger_tree[name]
            if isinstance(obj, DummyLog):
                self.logger_tree[name] = logger
                self._check_children(obj, logger)
                self._check_parents(logger)
                obj = None
        else:
            self.logger_tree[name] = logger
            self._check_parents(logger)
        _Global_and_Destruct_Lock.release()

        return obj

    # def spawn_logger(self, name: str):
    #     """_summary_"""

    #     logger = None
    #     _Global_and_Destruct_Lock.acquire()

    #     if name in self.logger_tree:
    #         logger = self.logger_tree[name]
    #         if isinstance(logger, DummyLog):
    #             obj = logger
    #             logger = Log(name)
    #             self.logger_tree[name] = logger
    #             self._check_children(obj, logger)
    #             self._check_parents(logger)
    #     else:
    #         logger = Log(name)
    #         self._check_parents(logger)
    #         self.logger_tree[name] = logger
    #     _Global_and_Destruct_Lock.release()

    #     return logger


def spawn_logger(
    name: str,
) -> "Log":
    """Spawn a logger within a hierarchy

    Parameters
    ----------
    name : str
        _description_

    Returns
    -------
    Log
        _description_
    """

    return Log(name)


class Logmeta(type):
    def __call__(
        cls,
        name: str,
        log_level: int = 2,
    ):
        """overriding default calling behaviour to accommodate
        the check in the logger tree
        """

        obj = cls.__new__(cls, name, log_level)
        cls.__init__(obj, name, log_level)

        res = Log.manager.resolve_logger_tree(obj)
        if res is not None:
            warn(
                f"{name} is already in use -> returning currently known object",
                UserWarning,
            )
            obj = res

        return obj


class Receiver:
    _sentinel = None

    def __init__(self, queue):
        """_summary_"""

        self._t = None
        self._handlers = []
        self.count = 0
        self.q = queue

    def _log(
        self,
        record: LogItem,
    ):
        """_summary_"""

        for handler in self._handlers:
            if record.level >= handler.level:
                handler.emit(record)

    def _waiting(self):
        while True:
            try:
                record = self.get(True)
                if record is self._sentinel:
                    break
                self._log(record)
                self.count += 1
            except queue.Empty:
                break

    def close(self):
        self.q.put_nowait(self._sentinel)
        self._t.join()
        self._t = None

    def close_handlers(self):
        for handler in self._handlers:
            handler.close()
            handler = None

    def get(
        self,
        block: bool = True,
    ):
        """_summary_"""

        return self.q.get(block=block)

    def add_handler(
        self,
        handler,
    ):
        """_summary_

        Parameters
        ----------
        handler : _type_
            _description_
        """

        self._handlers.append(handler)

    def start(self):
        self._t = t = threading.Thread(
            target=self._waiting,
            name="mp_logging_thread",
        )
        t.deamon = True
        t.start()


class Log(metaclass=Logmeta):
    """_summary_"""

    manager = LogManager()

    # def __new__(
    #     cls,
    #     name: str,
    #     log_level: int = 2,
    # ):

    #     obj = object.__new__(cls)
    #     obj.__init__(name, log_level)

    #     res = Log.manager.fit_external_logger(obj)
    #     if res is not None:
    #         warn(f"{name} is already in use -> returning currently known object", UserWarning)
    #         obj = res

    #     return obj

    def __init__(
        self,
        name: str,
        log_level: int = 2,
    ):
        """Logging!

        Parameters
        ----------
        name : str
            _description_
        log_level : int, optional
            _description_, by default 2
        """

        self._log_level = _Level(log_level)
        self.name = name
        self.bubble_up = True
        self.parent = None
        self._handlers = []

        _loggers[self.name] = self

    def __del__(self):
        pass

    def __repr__(self):
        _lvl_str = str(LogLevels(self.log_level)).split(".")[1]
        return f"<Log {self.name} level={_lvl_str}>"

    def __str__(self):
        _mem_loc = f"{id(self):#018x}".upper()
        return f"<{self.__class__.__name__} object at {_mem_loc}>"

    def _log(self, record):
        """Handles logging"""

        obj = self
        while obj:
            for logger in obj._handlers:
                if record.level < logger.level:
                    continue
                else:
                    logger.emit(record)
            if not obj.bubble_up:
                obj = None
            else:
                obj = obj.parent

    def handleLog(log_m):
        """A wrapper for logging messages"""

        def handle(self, *args, **kwargs):
            lvl, msg = log_m(self, *args, **kwargs)
            self._log(LogItem(level=lvl, msg=msg))

        return handle

    def add_c_handler(
        self,
        level: int = 2,
        name: str = None,
    ):
        """Add an outlet to the console

        Parameters
        ----------
        level : int, optional
            _description_, by default 2
        name : str, optional
            _description_, by default None
        """

        self._handlers.append(CHandler(level=level, name=name))

    def add_file_handler(
        self,
        dst: str,
        level: int = 2,
        filename: str = None,
    ):
        """Add an outlet to a file

        Parameters
        ----------
        dst : str
            _description_
        level : int, optional
            _description_, by default 2
        filename : str, optional
            _description_, by default None
        """

        self._handlers.append(FileHandler(dst=dst, level=level, name=filename))

    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(
        self,
        val: int,
    ):
        self._log_level = _Level(val)

    @handleLog
    def debug(self, msg: str):
        """_summary_"""

        return 1, msg

    @handleLog
    def info(self, msg: str):
        """_summary_"""

        return 2, msg

    @handleLog
    def warning(self, msg: str):
        """_summary_"""

        return 3, msg

    @handleLog
    def error(self, msg: str):
        """_summary_"""

        return 4, msg

    @handleLog
    def dead(self, msg: str):
        """_summary_"""

        return 5, msg

    def direct(self, msg):
        """_summary_"""

        self._log()


def setup_default_log(
    name: str,
    log_level: int,
    dst: str,
) -> Log:
    """_summary_

    Parameters
    ----------
    name : str
        _description_
    log_level : int
        _description_
    dst : str
        _description_

    Returns
    -------
    Log
        _description_

    Raises
    ------
    ValueError
        _description_
    """
    if len(name.split(".")) > 1:
        raise ValueError()

    obj = Log(name, log_level=log_level)

    obj.add_c_handler(level=log_level)
    obj.add_file_handler(
        dst,
        level=log_level,
        filename=name,
    )

    return obj


def setup_mp_log(
    queue: queue.Queue,
    name: str,
    log_level: int,
    dst: str = None,
):
    """_summary_

    Parameters
    ----------
    queue : queue.Queue
        _description_
    log_level : int
        _description_
    dst : str, optional
        _description_, by default None
    """

    obj = Receiver(queue)
    h = FileHandler(level=log_level, dst=dst, name=name)
    h.set_formatter(MessageFormatter("{asctime:20s}{message}"))
    obj.add_handler(h)
    return obj
