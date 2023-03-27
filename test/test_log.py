import pytest
from delft_fiat.log import StreamLogger, Log


def test_stream():
    assert 1 == 1


def test_log(tmpdir):
    log = Log("fiat")
    log.add_loggers(str(tmpdir))
    log.info("Start of test logging")
    log.warning("Warning about stuff")
    log.error("Something has really gone wrong...")
    log.dead("Bye")
