from delft_fiat.log import StreamLogger, Log, spawn_child_logger

import io
import pytest
from pathlib import Path


def test_stream():
    stream = io.StringIO()
    sl = StreamLogger(stream=stream)

    sl.emit("Hello!\n")
    sl.emit("Good day!\n")

    stream.seek(0)
    assert stream.readline().strip() == "Hello!"


def test_log(tmpdir):
    log = Log("fiat", log_level=2)
    log.add_loggers(
        str(tmpdir),
        cmd_stream=True,
    )
    child_log = spawn_child_logger("fiat.child")

    assert id(log) != id(child_log)

    log.debug("This message should not be output")
    log.info("Start of test logging")
    log.warning("Warning about stuff")
    log.error("Something has really gone wrong...")
    child_log.error("I also quit!")
    log.dead("Bye")

    del child_log
    del log

    fh = open(Path(str(tmpdir), "fiat.log"), mode="r")

    assert sum(1 for _ in fh) == 5
