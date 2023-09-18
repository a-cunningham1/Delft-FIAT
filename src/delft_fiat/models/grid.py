from delft_fiat.check import *
from delft_fiat.io import BufferTextHandler, open_grid
from delft_fiat.log import spawn_logger
from delft_fiat.models.base import BaseModel
from delft_fiat.models.util import grid_worker_exact
from delft_fiat.util import NEWLINE_CHAR

from concurrent.futures import ProcessPoolExecutor
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

        file = self._cfg.get("exposure.grid.file")
        logger.info(f"Reading exposure grid ('{file.name}')")
        kw = self._cfg.generate_kwargs("exposure.grid.settings")
        data = open_grid(file, **kw)
        ## checks
        logger.info("Executing exposure data checks...")
        check_grid_exact(self.hazard_grid, data)

        self.exposure_grid = data

    def resolve():
        pass

    def run(self):
        """_summary_"""

        grid_worker_exact(
            self._cfg,
            self.hazard_grid,
            1,
            self.vulnerability_data,
            self.exposure_grid,
        )
