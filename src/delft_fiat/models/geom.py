from delft_fiat.check import check_srs
from delft_fiat.gis import geom, overlay
from delft_fiat.gis.crs import get_srs_repr
from delft_fiat.io import (
    BufferTextHandler,
    GeomMemFileHandler,
    open_csv,
    open_exp,
    open_geom,
)
from delft_fiat.log import spawn_logger
from delft_fiat.models.base import BaseModel
from delft_fiat.models.util import geom_worker
from delft_fiat.util import NEWLINE_CHAR

import os
import time
from concurrent.futures import ProcessPoolExecutor, wait, as_completed
from multiprocessing import Process
from pathlib import Path

logger = spawn_logger("fiat.model.geom")


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

            if not check_srs(self.srs, data.get_srs(), path.name):
                logger.warning(
                    f"Spatial reference of {path.name} does not match the global spatial reference"
                )
                logger.info(f"Reprojecting {path.name} to {get_srs_repr(self.srs)}")
                data = geom.reproject(data, self.srs.ExportToWkt())
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
                        geom_worker,
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
                target=geom_worker,
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
