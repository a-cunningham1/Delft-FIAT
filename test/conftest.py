from fiat.cfg import ConfigReader
from fiat.io import open_geom, open_grid
from fiat.log import LogItem

import pytest
from pathlib import Path


@pytest.fixture
def settings_toml_event():
    return Path(Path.cwd(), ".testdata", "settings.toml")


@pytest.fixture
def settings_toml_risk():
    return Path(Path.cwd(), ".testdata", "settings_risk.toml")


@pytest.fixture
def cfg_event(settings_toml_event):
    c = ConfigReader(settings_toml_event)
    return c


@pytest.fixture
def mis_event():
    p = Path(Path.cwd(), ".testdata", "settings_missing.toml")
    return ConfigReader(p)


@pytest.fixture
def cfg_risk(settings_toml_risk):
    c = ConfigReader(settings_toml_risk)
    return c


@pytest.fixture
def gm(cfg_event):
    d = open_geom(cfg_event.get_path("exposure.geom.file1"))
    return d


@pytest.fixture
def gr_event(cfg_event):
    d = open_grid(cfg_event.get_path("hazard.file"))
    return d


@pytest.fixture
def gr_risk(cfg_risk):
    d = open_grid(cfg_risk.get_path("hazard.file"), var_as_band=True)
    return d


@pytest.fixture
def log1():
    obj = LogItem(level=2, msg="Hello!")
    return obj


@pytest.fixture
def log2():
    obj = LogItem(level=2, msg="Good Bye!")
    return obj
