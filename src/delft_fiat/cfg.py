from delft_fiat.util import GenericPathCheck, Path

import os
import tomli


class ConfigReader(dict):
    def __init__(
        self,
        file: str,
    ):
        # Set the root directory
        self._filepath = Path(file)
        self._path = self._filepath.parent

        # Load the config as a simple dictionary
        f = open(file, "rb")
        dict.__init__(self, tomli.load(f))
        f.close()

        # Do some checking concerning the file paths in the settings file
        for group in self.values():
            if not isinstance(group, dict):
                continue
            else:
                for key, item in group.items():
                    if key.endswith("file"):
                        path = GenericPathCheck(
                            item,
                            self._path,
                        )
                        group[key] = path

    def __repr__(self):
        return f"<ConfigReader object file='{self._filepath}'>"

    def get_model_type():
        pass

    def get_path(
        self,
        gr: str,
        item: str,
    ):
        """_Summary_"""

        return str(self[gr][item])


if __name__ == "__main__":
    c = ConfigReader(r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\Casus\settings.toml")
    pass
