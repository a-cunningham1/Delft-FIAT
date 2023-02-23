from delft_fiat.reader.util import DamageLookup, GenericFileCheck, Path

import os
import tomli


class ConfigReader:
    def __init__(
        self,
        file: str,
    ):
        self._Path = Path(file).parent
        f = open(file, "rb")
        self._config = tomli.load(f)
        f.close()

    def GetDamage(
        self,
        code: str,
    ):
        GenericFileCheck(self._config["damage"]["file"])
        pass

    def GetExposure():
        pass


if __name__ == "__main__":
    c = ConfigReader(r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\settings.toml")
    pass
