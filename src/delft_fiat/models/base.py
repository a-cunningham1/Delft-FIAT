from delft_fiat.io import open_csv, open_geom, open_grid

from abc import ABCMeta, abstractmethod
from osgeo import osr


class BaseModel(metaclass=ABCMeta):
    def __init__(
        self,
        cfg: "ConfigReader",
    ):
        """_summary_"""

        self._cfg = cfg
        self._args = []

        self.srs = osr.SpatialReference()
        self.srs.SetFromUserInput(self._cfg.get("global.crs"))

        # Declarations
        self._exposure_data = None
        self._exposure_geoms = None
        self._exposure_grid = None
        self._hazard_grid = None
        self._vulnerability_data = None
        self._outhandler = None

        self._read_hazard_grid()
        self._read_vulnerability_data()

    @abstractmethod
    def __del__(self):
        self.srs = None

    def __repr__(self):
        return f"<{self.__class__.__name__} object at {id(self):#018x}>"

    def _read_hazard_grid(self):
        data = open_grid(self._cfg.get_path("hazard.grid_file"))
        ## checks

        self._hazard_grid = data

    def _read_vulnerability_data(self):
        data = open_csv(self._cfg.get_path("vulnerability.dbase_file"))
        ## checks

        self._vulnerability_data = data
        self._args.append(self._vulnerability_data)

    @abstractmethod
    def run():
        pass
