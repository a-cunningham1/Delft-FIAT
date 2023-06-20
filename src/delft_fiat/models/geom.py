from delft_fiat.gis import geom, overlay
from delft_fiat.io import BufferTextHandler, GeomMemFileHandler, open_csv, open_geom
from delft_fiat.log import spawn_logger
from delft_fiat.models.base import BaseModel
from delft_fiat.models.calc import get_inundation_depth, get_damage_factor
from delft_fiat.util import _pat, replace_empty

import os
import time
from concurrent.futures import ProcessPoolExecutor, wait, as_completed
from io import BufferedWriter
from math import isnan
from multiprocessing import Process
from pathlib import Path

logger = spawn_logger("fiat.model.geom")


def worker(
    writer: BufferTextHandler,
    geom_writer: GeomMemFileHandler,
    haz: "GridSource",
    idx: int,
    vul: "Table",
    exp: "TableLazy",
    gm: "GeomSource",
):
    """_summary_

    Parameters
    ----------
    writer : BufferTextHandler
        _description_
    haz : GridSource
        _description_
    idx : int
        _description_
    vul : Table
        _description_
    exp : TableLazy
        _description_
    gm : GeomSource
        _description_
    """

    header = (
        ",".join(exp.columns).encode()
        + b","
        + ",".join(exp._extra_columns.values()).encode()
        + b"\r\n"
    )
    writer.write(header)

    for ft in gm:
        row = b""

        ft_info_raw = exp[ft.GetField(0)]
        ft_info = replace_empty(_pat.split(ft_info_raw))
        ft_info = [x(y) for x, y in zip(exp.dtypes, ft_info)]

        if ft_info[exp._columns["Extraction Method"]].lower() == "area":
            res = overlay.clip(haz[idx], haz.get_srs(), haz.get_geotransform(), ft)
        else:
            res = overlay.pin(haz[idx], haz.get_geotransform(), geom.point_in_geom(ft))
        inun = get_inundation_depth(
            res,
            "DEM",
            ft_info[exp._columns["Ground Floor Height"]],
        )

        row += ft_info_raw

        ft_new_info = {}
        for key, col in exp.damage_function.items():
            if isnan(inun[0]) or ft_info[col] == "nan":
                _d = ""
            else:
                _df = vul[round(inun[0], 2), ft_info[col]]
                _d = _df * ft_info[exp.max_potential_damage[key]]

            ft_new_info[exp._extra_columns[key]] = _d
            row += f",{_d}".encode()

        geom_writer.write_feature(ft, ft_new_info)
        row += b"\r\n"
        writer.write(row)

    writer.flush()


class GeomModel(BaseModel):
    _method = {
        "area": overlay.clip,
        "centroid": overlay.pin,
    }

    def __init__(
        self,
        cfg: "ConfigReader",
    ):
        """_summary_"""

        super().__init__(cfg)

        self._read_exposure_data()
        self._read_exposure_geoms()
        self._vulnerability_data.upscale(0.01, inplace=True)

    def __del__(self):
        BaseModel.__del__(self)

    def _read_exposure_data(self):
        """_summary_"""

        path = self._cfg.get("exposure.vector.csv")
        logger.info(f"Reading exposure data ('{path.name}')")
        data = open_csv(path, index="Object ID", large=True)
        ##checks
        self._exposure_data = data
        self._exposure_data.search_extra_meta(
            ("Damage Function:", "Max Potential Damage")
        )

    def _read_exposure_geoms(self):
        """_summary_"""

        _d = {}
        _found = [item for item in list(self._cfg) if "exposure.vector.file" in item]
        for file in _found:
            path = self._cfg.get(file)
            logger.info(
                f"Reading exposure geometry '{file.split('.')[-1]}' ('{path.name}')"
            )
            data = open_geom(str(path))
            ##checks
            if not (
                self.srs.IsSame(data.get_srs())
                or self.srs.ExportToWkt() == data.get_srs().ExportToWkt()
            ):
                data = geom.reproject(data, data.get_srs().ExportToWkt())
            _d[file.rsplit(".", 1)[1]] = data
        self._exposure_geoms = _d

    def run(self):
        """_summary_"""

        out_csv = "output.csv"
        if "output.csv.name" in self._cfg:
            out_csv = self._cfg["output.csv.name"]

        writer = BufferTextHandler(
            Path(self._cfg["output.path"], out_csv),
            buffer_size=100000,
        )

        out_geom = "spatial.gpkg"
        if "output.geom.name1" in self._cfg:
            out_geom = self._cfg["output.geom.name1"]

        geom_writer = GeomMemFileHandler(
            Path(self._cfg["output.path"], out_geom),
            self.srs,
            self._exposure_geoms["file1"].layer.GetLayerDefn(),
            self._exposure_data._extra_columns_meta,
        )

        if self._hazard_grid.count > 1:
            pcount = min(os.cpu_count(), self._hazard_grid.count)
            with ProcessPoolExecutor(max_workers=pcount) as Pool:
                for idx in range(self._hazard_grid.count):
                    p = Pool.submit(
                        worker,
                        writer,
                        self._hazard_grid,
                        1,
                        self._vulnerability_data,
                        self._exposure_data,
                        self._exposure_geoms["file1"],
                    )
                for f in as_completed([p]):
                    print(f.result())

        else:
            worker(
                writer,
                geom_writer,
                self._hazard_grid,
                1,
                self._vulnerability_data,
                self._exposure_data,
                self._exposure_geoms["file1"],
            )

        geom_writer.dump2drive()
        del writer
        del geom_writer
