from delft_fiat.check import (
    check_global_crs,
    check_hazard_subsets,
    check_srs,
)
from delft_fiat.gis import grid
from delft_fiat.gis.crs import get_srs_repr
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
        logger.info(f"Using settings from '{self._cfg.filepath}'")

        # Declarations
        self.srs = None
        self._exposure_data = None
        self._exposure_geoms = None
        self._exposure_grid = None
        self._hazard_grid = None
        self._vulnerability_data = None
        self._outhandler = None

        self._set_model_srs()
        self._read_hazard_grid()
        self._read_vulnerability_data()

    @abstractmethod
    def __del__(self):
        self.srs = None

    def __repr__(self):
        return f"<{self.__class__.__name__} object at {id(self):#018x}>"

    @abstractmethod
    def _clean_up(self):
        pass

    def _read_hazard_grid(self):
        path = self._cfg.get("hazard.file")
        logger.info(f"Reading hazard data ('{path.name}')")
        kw = self._cfg.generate_kwargs("hazard.multiband")
        data = open_grid(path, **kw)
        ## checks
        logger.info("Executing hazard checks...")
        check_hazard_subsets(
            data.subset_dict,
            path,
        )
        if not check_srs(self.srs, data.get_srs(), path.name):
            logger.warning(
                f"Spatial reference of '{path.name}' ('{get_srs_repr(data.get_srs())}') \
does not match the model spatial reference ('{get_srs_repr(self.srs)}')"
            )
            logger.info(f"Reprojecting '{path.name}' to '{get_srs_repr(self.srs)}'")
            data = grid.reproject(data, self.srs.ExportToWkt())
        ## When all is done, add it
        self._hazard_grid = data

    def _read_vulnerability_data(self):
        path = self._cfg.get("vulnerability.file")
        logger.info(f"Reading vulnerability curves ('{path.name}')")
        data = open_csv(str(path), index="water depth")
        ## checks
        logger.info("Executing vulnerability checks...")

        self._vulnerability_data = data

    def _set_model_srs(self):
        """_summary_"""

        _srs = self._cfg.get("global.crs")
        path = self._cfg.get("hazard.file")
        if _srs is not None:
            self.srs = osr.SpatialReference()
            self.srs.SetFromUserInput(_srs)
        else:
            ## Inferring by 'sniffing'
            kw = self._cfg.generate_kwargs("hazard.multiband")

            gm = open_grid(
                str(path),
                **kw,
            )

            _srs = gm.get_srs()
            if _srs is None:
                if "hazard.crs" in self._cfg:
                    _srs = osr.SpatialReference()
                    _srs.SetFromUserInput(self._cfg.get("hazard.crs"))
            self.srs = _srs

        ## Simple check to see if it's not None
        check_global_crs(
            self.srs,
            self._cfg.filepath.name,
            path.name,
        )

        logger.info(f"Model srs set to: '{get_srs_repr(self.srs)}'")

    @abstractmethod
    def run():
        pass
