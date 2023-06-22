from delft_fiat.gis import geom, overlay
from delft_fiat.io import (
    BufferTextHandler,
    GeomMemFileHandler,
    open_csv,
    open_exp,
    open_geom,
)
from delft_fiat.log import spawn_logger
from delft_fiat.models.base import BaseModel
from delft_fiat.models.calc import get_inundation_depth, get_damage_factor
from delft_fiat.util import _pat, NEWLINE_CHAR, replace_empty

import os
import time
from concurrent.futures import ProcessPoolExecutor, wait, as_completed
from io import BufferedWriter
from math import isnan
from multiprocessing import Process
from pathlib import Path

logger = spawn_logger("fiat.model.geom")


def worker(
    path: Path,
    haz: "GridSource",
    idx: int,
    exp: "TableLazy",
    exp_geom: "GeomSource",
    vul: "Table",
):
    """_summary_"""

    _band_name = haz.get_band_name(idx)

    writer = BufferTextHandler(
        Path(path, f"{_band_name}.dat"),
        buffer_size=100000,
    )
    header = (
        f"{exp.meta['index_name']},".encode()
        + ",".join(exp.create_specific_columns(_band_name)).encode()
        + NEWLINE_CHAR.encode()
    )
    writer.write(header)

    for ft in exp_geom:
        row = b""

        ft_info_raw = exp[ft.GetField(0)]
        ft_info = replace_empty(_pat.split(ft_info_raw))
        ft_info = [x(y) for x, y in zip(exp.dtypes, ft_info)]
        row += f"{ft_info[exp.index_col]}".encode()

        if ft_info[exp._columns["Extraction Method"]].lower() == "area":
            res = overlay.clip(haz[idx], haz.get_srs(), haz.get_geotransform(), ft)
        else:
            res = overlay.pin(haz[idx], haz.get_geotransform(), geom.point_in_geom(ft))
        inun, redf = get_inundation_depth(
            res,
            "DEM",
            ft_info[exp._columns["Ground Floor Height"]],
        )
        row += f",{inun},{redf}".encode()

        _td = 0
        for key, col in exp.damage_function.items():
            if isnan(inun) or ft_info[col] == "nan":
                _d = ""
            else:
                _df = vul[round(inun, 2), ft_info[col]]
                _d = _df * ft_info[exp.max_potential_damage[key]] * redf
                _td += _d

            row += f",{_d}".encode()

        row += f",{_td}".encode()

        row += NEWLINE_CHAR.encode()
        writer.write(row)

    writer.flush()
    writer = None


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

    def _clean_up(self):
        pass

    def _read_exposure_data(self):
        """_summary_"""

        path = self._cfg.get("exposure.geom.csv")
        logger.info(f"Reading exposure data ('{path.name}')")
        data = open_exp(path, index="Object ID")
        ##checks

        self._exposure_data = data

    def _read_exposure_geoms(self):
        """_summary_"""

        _d = {}
        _found = [item for item in list(self._cfg) if "exposure.geom.file" in item]
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

    def patch_up(
        self,
    ):
        """_summary_"""

        _exp = self._exposure_data
        _gm = self._exposure_geoms["file1"]
        _files = {}
        header = b""

        out_csv = "output.csv"
        if "output.csv.name" in self._cfg:
            out_csv = self._cfg["output.csv.name"]

        writer = BufferTextHandler(
            Path(self._cfg["output.path"], out_csv),
            buffer_size=100000,
        )
        header += ",".join(_exp.columns).encode() + b","
        out_geom = "spatial.gpkg"
        if "output.geom.name1" in self._cfg:
            out_geom = self._cfg["output.geom.name1"]

        geom_writer = GeomMemFileHandler(
            Path(self._cfg["output.path"], out_geom),
            self.srs,
            self._exposure_geoms["file1"].layer.GetLayerDefn(),
        )

        _paths = Path(self._cfg.get("output.path.tmp")).glob("*.dat")

        for p in _paths:
            _d = open_csv(p, index=_exp.meta["index_name"], large=True)
            header += ",".join(_d.columns[1:]).encode()
            geom_writer.set_fields(_exp.create_specific_meta(p.stem))
            _files[p.stem] = _d
            _d = None

        header += NEWLINE_CHAR.encode()
        writer.write(header)

        for ft in _gm:
            row = b""

            oid = ft.GetField(0)
            row += _exp[oid].strip() + b","
            for key, item in _files.items():
                _data = item[oid].strip().split(b",", 1)[1]
                row += _data
                geom_writer.write_feature(
                    ft,
                    fmap=dict(
                        zip(
                            _exp.create_specific_columns(p.stem),
                            [num.decode() for num in _data.split(b",")],
                        )
                    ),
                )
            row += NEWLINE_CHAR.encode()

            writer.write(row)

        writer.flush()
        writer = None

        geom_writer.dump2drive()
        geom_writer = None

    def run(
        self,
    ):
        """_summary_"""

        if self._hazard_grid.count > 1:
            pcount = min(os.cpu_count(), self._hazard_grid.count)
            with ProcessPoolExecutor(max_workers=pcount) as Pool:
                for idx in range(self._hazard_grid.count):
                    p = Pool.submit(
                        worker,
                        self._hazard_grid,
                        idx,
                        self._vulnerability_data,
                        self._exposure_data,
                        self._exposure_geoms["file1"],
                    )
                for f in as_completed([p]):
                    print(f.result())

        else:
            p = Process(
                target=worker,
                args=(
                    self._cfg.get("output.path.tmp"),
                    self._hazard_grid,
                    1,
                    self._exposure_data,
                    self._exposure_geoms["file1"],
                    self._vulnerability_data,
                ),
            )
            p.start()
            p.join()
        self.patch_up()
