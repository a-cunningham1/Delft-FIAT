from pathlib import Path

from fiat.cfg import ConfigReader


def test_settings():
    ConfigReader(Path(Path.cwd(), ".testdata", "settings.toml"))
    pass
