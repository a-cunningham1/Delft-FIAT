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
        + ",".join(exp._extra_columns).encode()
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

        for key, col in exp.damage_function.items():
            if isnan(inun[0]) or ft_info[col] == "nan":
                _d = ""
            else:
                _df = vul[round(inun[0], 2), ft_info[col]]
                _d = _df * ft_info[exp.max_potential_damage[key]]

            row += f",{_d}".encode()
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
        super().__init__(cfg)

        self._geoms = True
        self._read_exposure_data()
        self._read_exposure_geoms()
        self._vulnerability_data.upscale(0.01, inplace=True)

    def __del__(self):
        BaseModel.__del__(self)

    def _read_exposure_data(self):
        path = self._cfg.get("exposure.vector.csv")
        logger.info(f"Reading exposure data ('{path.name}')")
        data = open_csv(path, index="Object ID", large=True)
        ##checks
        self._exposure_data = data
        self._exposure_data.search_extra_meta(
            ("Damage Function:", "Max Potential Damage")
        )

    def _read_exposure_geoms(self):
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
                self._hazard_grid,
                1,
                self._vulnerability_data,
                self._exposure_data,
                self._exposure_geoms["file1"],
            )
        del writer
