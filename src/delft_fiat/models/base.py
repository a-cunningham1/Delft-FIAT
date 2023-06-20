from delft_fiat.check import check_hazard_subsets
from delft_fiat.io import open_csv, open_geom, open_grid
from delft_fiat.log import spawn_logger

from abc import ABCMeta, abstractmethod
from osgeo import osr

logger = spawn_logger("fiat.model")


class BaseModel(metaclass=ABCMeta):
    def __init__(
        self,
        cfg: "ConfigReader",
    ):
        """_summary_"""

        self._cfg = cfg

        _srs = self._cfg.get("global.crs")
        self.srs = osr.SpatialReference()
        self.srs.SetFromUserInput(_srs)
        logger.info(f"Global srs set to: {_srs}")

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
        path = self._cfg.get("hazard.file")
        logger.info(f"Reading hazard data ('{path.name}')")
        data = open_grid(path)
        ## checks
        logger.info("Executing hazard checks...")
        check_hazard_subsets(
            data.subset_dict,
            path,
        )
        ## When all is done, add it
        self._hazard_grid = data

    def _read_vulnerability_data(self):
        path = self._cfg.get("vulnerability.file")
        logger.info(f"Reading vulnerability curves ('{path.name}')")
        data = open_csv(str(path), index="water depth")
        ## checks
        logger.info("Executing vulnerability checks...")

        self._vulnerability_data = data

    @abstractmethod
    def run():
        pass
