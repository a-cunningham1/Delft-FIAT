from delft_fiat.models.base import BaseModel

import time
from osgeo import gdal, ogr


class GeomModel(BaseModel):
    def __init__(
        self,
        cfg: "cfg.ConfigReader",
    ):
        super().__init__(cfg)
        pass


if __name__ == "__main__":
    from delft_fiat.cfg import ConfigReader

    a = GeomModel(
        ConfigReader(r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\Casus\settings.toml")
    )
    pass
