from delft_fiat.check import check_config_data
from delft_fiat.util import (
    Path,
    create_hidden_folder,
    flatten_dict,
    generic_folder_check,
    generic_path_check,
)

import os
import tomli


class ConfigReader(dict):
    def __init__(
        self,
        file: str,
    ):
        # Set the root directory
        self.filepath = Path(file)
        self.path = self.filepath.parent

        # Load the config as a simple flat dictionary
        f = open(file, "rb")
        dict.__init__(self, flatten_dict(tomli.load(f), "", "."))
        f.close()

        # Ensure the output directory is there
        _p = Path(self["output.path"])
        if not _p.is_absolute():
            _p = Path(self.path, _p)
        generic_folder_check(_p)
        self["output.path"] = _p

        # Create the hidden temporary folder
        _ph = Path(_p, ".tmp")
        create_hidden_folder(_ph)
        self["output.path.tmp"] = _ph

        # Do some checking concerning the file paths in the settings file
        for key, item in self.items():
            if key.endswith(("file", "csv")) or key.rsplit(".", 1)[1].startswith(
                "file"
            ):
                path = generic_path_check(
                    item,
                    self.path,
                )
                self[key] = path
            else:
                if isinstance(item, str):
                    self[key] = item.lower()

    def __repr__(self):
        return f"<ConfigReader object file='{self.filepath}'>"

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

    def generate_kwargs(
        self,
        base: str,
    ):
        """_summary_"""

        keys = [item for item in list(self) if base in item]
        kw = {key.split(".")[-1]: self[key] for key in keys}

        return kw
