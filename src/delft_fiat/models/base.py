from delft_fiat.io import open_csv, open_geom
from delft_fiat.models.util import DamageLookup

from abc import ABCMeta, abstractmethod


class BaseModel(metaclass=ABCMeta):
    def __init__(self, cfg: "cfg.ConfigReader"):
        # Declarations
        self.hazard_data = None
        self.exposure_geoms = None
        self.exposure_base = None
        self.damage_data = None
        self._cfg = cfg

    def read_damage_files():
        pass

    def read_hazard_files():
        pass

    def read_exposure_files(self):
        return open_geom()

    def get_damage_curve(
        self,
        code: str,
    ) -> dict:
        path, method = DamageLookup(
            self._cfg["damage"]["file"],
            code,
            self._cfg._path,
        )
        c = open_csv(path)
        return c

    def get_exposure(
        self,
        bla,
    ):
        pass

    def get_objects():
        pass

    @abstractmethod
    def run():
        pass


if __name__ == "__main__":
    from delft_fiat.cfg import ConfigReader

    a = BaseModel(ConfigReader(r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\settings.toml"))
    pass
