from delft_fiat.io import FileHandler, ReadCSV
from delft_fiat.util import GenericPathCheck, Path
from delft_fiat.reader.util import DamageLookup

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
        for group in self._config.values():
            if not isinstance(group, dict):
                continue
            else:
                for key, item in group.items():
                    if key.endswith("file"):
                        path = GenericPathCheck(
                            item,
                            self._Path,
                        )
                        group[key] = path

    def GetDamageCurve(
        self,
        code: str,
    ) -> dict:
        path, method = DamageLookup(
            self._config["damage"]["dbase_file"],
            code,
            self._Path,
        )
        c = ReadCSV(path)
        return c

    def GetExposure(
        self,
        bla,
    ):
        pass

    def GetObjects():
        pass


if __name__ == "__main__":
    c = ConfigReader(r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\settings.toml")
    pass
