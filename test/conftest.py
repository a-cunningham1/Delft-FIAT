from delft_fiat.cfg import ConfigReader
from delft_fiat.io import open_geom, open_grid

import pytest
from pathlib import Path


@pytest.fixture
def settings_toml():
    return Path(Path.cwd(), ".testdata", "settings.toml")


@pytest.fixture
def cfg(settings_toml):
    c = ConfigReader(settings_toml)
    return c


@pytest.fixture
def gm(cfg):
    d = open_geom(cfg.get_path("exposure.vector.file1"))
    return d


@pytest.fixture
def gr(cfg):
    d = open_grid(cfg.get_path("hazard.file"))
    return d
