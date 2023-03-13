import pytest
from delft_fiat.log import StreamLogger, Log


def test_stream():
    assert 1 == 1


def test_log(tmpdir):
    log = Log(str(tmpdir), "Delft_fiat")
    log.Info("Start of test logging")
    log.Warning("Warning about stuff")
    log.Error("Something has really gone wrong...")
    log.Dead("Bye")
