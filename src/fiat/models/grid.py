from fiat.check import *
from fiat.io import BufferTextHandler, open_grid
from fiat.log import spawn_logger
from fiat.models.base import BaseModel
from fiat.models.util import grid_worker_exact
from fiat.util import NEWLINE_CHAR

import time
from concurrent.futures import ProcessPoolExecutor, wait
from multiprocessing import Process, get_context

logger = spawn_logger("fiat.model.grid")


class GridModel(BaseModel):
    def __init__(
        self,
        cfg: "ConfigReader",
    ):
        """_summary_"""

        super().__init__(cfg)

        self._read_exposure_grid()

    def __del__(self):
        BaseModel.__del__(self)

    def _clean_up(self):
        pass

    def _read_exposure_grid(self):
        """_summary_"""

        file = self.cfg.get("exposure.grid.file")
        logger.info(f"Reading exposure grid ('{file.name}')")
        # Set the extra arguments from the settings file
        kw = {}
        kw.update(
            self.cfg.generate_kwargs("global.grid"),
        )
        kw.update(
            self.cfg.generate_kwargs("exposure.grid.settings"),
        )
        data = open_grid(file, **kw)
        ## checks
        logger.info("Executing exposure data checks...")
        check_grid_exact(self.hazard_grid, data)

        self.exposure_grid = data

    def resolve():
        """_summary_"""

        pass

    def run(self):
        """_summary_"""

        _nms = self.cfg.get("hazard.band_names")

        if self.hazard_grid.count > 1:
            pcount = min(self.max_threads, self.hazard_grid.count)
            futures = []
            with ProcessPoolExecutor(max_workers=pcount) as Pool:
                _s = time.time()
                for idx in range(self.hazard_grid.count):
                    logger.info(
                        f"Submitting a job for the calculations in regards to band: '{_nms[idx]}'"
                    )
                    fs = Pool.submit(
                        grid_worker_exact,
                        self.cfg,
                        self.hazard_grid,
                        idx + 1,
                        self.vulnerability_data,
                        self.exposure_grid,
                    )
                    futures.append(fs)
            logger.info("Busy...")
            wait(futures)

        else:
            logger.info(f"Submitting a job for the calculations in a seperate process")
            _s = time.time()
            p = Process(
                target=grid_worker_exact,
                args=(
                    self.cfg,
                    self.hazard_grid,
                    1,
                    self.vulnerability_data,
                    self.exposure_grid,
                ),
            )
            p.start()
            logger.info("Busy...")
            p.join()
        _e = time.time() - _s

        logger.info(f"Calculations time: {round(_e, 2)} seconds")
        logger.info(f"Output generated in: '{self.cfg['output.path']}'")
        logger.info("Grid calculation are done!")
