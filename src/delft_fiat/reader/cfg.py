from delft_fiat.io import ReadCSV
from delft_fiat.reader.util import DamageLookup, GenericFileCheck, Path

import os
import tomli


class ConfigReader:
    def __init__(
        self,
        file: str,
    ):
        # Set the root directory
        self._Path = Path(file).parent

        # Load the config as a simple dictionary
        f = open(file, "rb")
        self._config = tomli.load(f)
        f.close()

        # Do some checking concerning the file paths in the settings file
        for item in self._config.values():
            if not isinstance(item, dict):
                continue
            if "file" in item:
                path = GenericFileCheck(
                    item["file"],
                    self._Path,
                )
                item["file"] = path

    def GetDamageCurve(
        self,
        code: str,
    ) -> dict:
        path, method = DamageLookup(
            self._config["damage"]["file"],
            code,
            self._Path,
        )
        print(path)
        c = ReadCSV(path)
        return c

    def GetExposure():
        pass


if __name__ == "__main__":
    c = ConfigReader(r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\settings.toml")
    pass
