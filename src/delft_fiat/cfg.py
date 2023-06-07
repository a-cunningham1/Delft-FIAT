from delft_fiat.check import check_config_data
from delft_fiat.util import Path, flatten_dict, generic_folder_check, generic_path_check

import os
import tomli


class ConfigReader(dict):
    def __init__(
        self,
        file: str,
    ):
        # Set the root directory
        self._filepath = Path(file)
        self.path = self._filepath.parent

        # Load the config as a simple flat dictionary
        f = open(file, "rb")
        dict.__init__(self, flatten_dict(tomli.load(f), "", "."))
        f.close()

        # Ensure the output directory is there
        _p = Path(self["global.output_dir"])
        if not _p.is_absolute():
            _p = Path(self.path, _p)
        generic_folder_check(_p)
        self["global.output_dir"] = _p

        # Do some checking concerning the file paths in the settings file
        for key, item in self.items():
            if key.endswith("file") or key.rsplit(".", 1)[1].startswith("file"):
                path = generic_path_check(
                    item,
                    self.path,
                )
                self[key] = path
            else:
                if isinstance(item, str):
                    self[key] = item.lower()

    def __repr__(self):
        return f"<ConfigReader object file='{self._filepath}'>"

    def get_model_type(
        self,
    ):
        """_Summary_"""

        if "exposure.geom_file" in self:
            return 0
        else:
            return 1

    def get_path(
        self,
        key: str,
    ):
        """_Summary_"""

        return str(self[key])
