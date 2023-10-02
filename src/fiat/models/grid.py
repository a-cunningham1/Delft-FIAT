from fiat.io import BufferTextHandler, open_grid
from fiat.log import spawn_logger
from fiat.models.base import BaseModel
from fiat.util import _pat, replace_empty

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, get_context

logger = spawn_logger("fiat.model.grid")


def worker(haz, vul, exp):
    pass


class GridModel(BaseModel):
    def __init__(
        self,
        cfg: "ConfigReader",
    ):
        """_summary_"""
        pass

    def __del__(self):
        BaseModel.__del__(self)

    def _read_exposure_grid(self):
        """_summary_"""

        path = self._cfg.get("exposure.grid.file")
        data = open_grid(path)
        ## checks

        self._exposure_grid = data

    def run(self):
        """_summary_"""

        worker()
