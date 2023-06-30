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
from delft_fiat.models.calc import calc_risk
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

    def __del__(self):
        BaseModel.__del__(self)

    def _clean_up(self):
        """_summary_"""

        _p = self._cfg.get("output.path.tmp")
        for _f in _p.glob("*"):
            os.unlink(_f)
        os.rmdir(_p)

    def _read_exposure_data(self):
        """_summary_"""

        path = self._cfg.get("exposure.geom.csv")
        logger.info(f"Reading exposure data ('{path.name}')")
        data = open_exp(path, index="Object ID")
        ##checks
        logger.info("Executing exposure data checks...")

        ## Information for output
        _ex = None
        if self._cfg["hazard.risk"]:
            _ex = ["Risk (EAD)"]
        cols = data.create_all_columns(
            self._cfg.get("hazard.band_names"),
            _ex,
        )
        self._cfg["output.new_columns"] = cols

        ## When all is done, add it
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
            logger.info("Executing exposure geometry checks...")

            if not check_srs(self.srs, data.get_srs(), path.name):
                logger.warning(
                    f"Spatial reference of '{path.name}' ('{get_srs_repr(data.get_srs())}') \
does not match the model spatial reference ('{get_srs_repr(self.srs)}')"
                )
                logger.info(f"Reprojecting '{path.name}' to '{get_srs_repr(self.srs)}'")
                data = geom.reproject(data, self.srs.ExportToWkt())
            ## Add to the dict
            _d[file.rsplit(".", 1)[1]] = data
        ## When all is done, add it
        self._exposure_geoms = _d

    def _patch_up(
        self,
    ):
        """_summary_"""

        _exp = self._exposure_data
        _gm = self._exposure_geoms
        _risk = self._cfg.get("hazard.risk")
        _rp_coef = self._cfg.get("hazard.rp_coefficients")
        _new_cols = self._cfg["output.new_columns"]
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
        header += ",".join(_new_cols).encode()
        header += NEWLINE_CHAR.encode()
        writer.write(header)

        _paths = Path(self._cfg.get("output.path.tmp")).glob("*.dat")

        for p in _paths:
            _d = open_csv(p, index=_exp.meta["index_name"], large=True)
            _files[p.stem] = _d
            _d = None

        for key, gm in _gm.items():
            _add = key[-1]
            out_geom = f"spatial{_add}.gpkg"
            if f"output.geom.name{_add}" in self._cfg:
                out_geom = self._cfg[f"output.geom.name{_add}"]

            geom_writer = GeomMemFileHandler(
                Path(self._cfg["output.path"], out_geom),
                self.srs,
                gm.layer.GetLayerDefn(),
            )

            geom_writer.create_fields(zip(_new_cols, ["float"] * len(_new_cols)))

            for ft in gm:
                row = b""

                oid = ft.GetField(0)
                row += _exp[oid].strip()
                vals = []

                for item in _files.values():
                    row += b","
                    _data = item[oid].strip().split(b",", 1)[1]
                    row += _data
                    _val = [float(num.decode()) for num in _data.split(b",")]
                    vals += _val

                if _risk:
                    ead = round(
                        calc_risk(_rp_coef, vals[-1 :: -_exp._dat_len]),
                        self._rounding,
                    )
                    row += f",{ead}".encode()
                    vals.append(ead)
                row += NEWLINE_CHAR.encode()
                writer.write(row)
                geom_writer.add_feature(
                    ft,
                    dict(zip(_new_cols, vals)),
                )

            geom_writer.dump2drive()
            geom_writer = None

        writer.flush()
        writer = None

    def run(
        self,
    ):
        """_summary_"""

        if self._hazard_grid.count > 1:
            pcount = min(os.cpu_count(), self._hazard_grid.count)
            futures = []
            with ProcessPoolExecutor(max_workers=pcount) as Pool:
                for idx in range(self._hazard_grid.count):
                    fs = Pool.submit(
                        geom_worker,
                        self._cfg,
                        self._hazard_grid,
                        idx + 1,
                        self._vulnerability_data,
                        self._exposure_data,
                        self._exposure_geoms,
                    )
                    futures.append(fs)
            wait(futures)
            # for p in p_s:
            #     p.join()
        else:
            p = Process(
                target=geom_worker,
                args=(
                    self._cfg,
                    self._hazard_grid,
                    1,
                    self._vulnerability_data,
                    self._exposure_data,
                    self._exposure_geoms,
                ),
            )
            p.start()
            p.join()
        self._patch_up()

        if not self._keep_temp:
            self._clean_up()
