from delft_fiat.gis import geom, overlay
from delft_fiat.io import open_csv, open_geom
from delft_fiat.models.base import BaseModel
from delft_fiat.models.calc import get_inundation_depth, get_damage_factor

import os
import time
from concurrent.futures import ProcessPoolExecutor
from osgeo import gdal, ogr


def worker_coord(haz, idx, vul, exp):
    pass


def worker_geoms(haz, idx, vul, exp_data, exp):
    for ft in exp:
        ft_info = exp_data[ft.GetField(0)]
        ft_info = [x(y) for x, y in zip(exp_data.dtypes, ft_info)]
        res = overlay.clip(haz[idx], haz.get_srs(), haz.get_geotransform(), ft)
        inun = get_inundation_depth(
            res,
            "DEM",
            float(ft_info[exp_data.header_index["Ground Floor Height"]]),
        )
        get_damage_factor(
            inun[0],
            vul[ft_info[exp_data.header_index["Damage Function: struct"]]],
        )
        pass


class GeomModel(BaseModel):
    _method = {
        "area": overlay.clip,
        "average": overlay.pin,
    }

    def __init__(
        self,
        cfg: "ConfigReader",
    ):
        super().__init__(cfg)

        self._geoms = True
        self._read_exposure_data()
        if self._geoms:
            self._read_exposure_geoms()

    def __del__(self):
        BaseModel.__del__(self)

    def _read_exposure_data(self):
        data = open_csv(self._cfg.get("exposure.dbase_file"), large=True)
        ##checks
        self._exposure_data = data
        self._args.append(self._exposure_data)

    def _read_exposure_geoms(self):
        data = open_geom(self._cfg.get_path("exposure.geom_file"))
        ##checks
        if not (
            self.srs.IsSame(data.get_srs())
            or self.srs.ExportToWkt() == data.get_srs().ExportToWkt()
        ):
            data = geom.reproject(data, data.get_srs().ExportToWkt())
        self._exposure_geoms = data
        self._args.append(self._exposure_geoms)

    def run(self):
        """_summary_"""

        func = worker_geoms
        if not self._geoms:
            func = worker_coord

        if self._hazard_grid.count > 1:
            pcount = min(os.cpu_count, self._hazard_grid.count)
            with ProcessPoolExecutor(max_workers=pcount) as Pool:
                for idx in range(self._hazard_grid.count):
                    Pool.submit(
                        func,
                        *[self._hazard_grid, idx, *self._args],
                    )
        else:
            func(self._hazard_grid, 1, *self._args)
