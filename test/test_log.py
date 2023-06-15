from delft_fiat.log import CMDStream, Log, spawn_logger

import io
import pytest
from pathlib import Path


def test_stream():
    stream = io.StringIO()
    sl = CMDStream(stream=stream)

    sl.emit("Hello!\n")
    sl.emit("Good day!\n")

    stream.seek(0)
    assert stream.readline().strip() == "Hello!"


def test_log(tmpdir):
    log = Log("fiat", log_level=2)
    log.add_cmd_stream(
        level=2,
    )
    log.add_file_stream(
        str(tmpdir),
        filename="fiat",
    )
    child_log = spawn_logger("fiat.child")

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
