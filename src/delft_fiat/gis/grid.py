from delft_fiat.io import open_grid

import gc
import os
from osgeo import gdal, osr
from pathlib import Path


def reproject(
    gs: "GridSource",
    crs: str,
) -> object:
    """_summary_

    Parameters
    ----------
    gs : GridSource
        _description_
    crs : str
        _description_

    Returns
    -------
    object
        _description_
    """

    fname_int = Path(gs.path.parent, f"{gs.path.stem}_repr.tif")
    fname = Path(gs.path.parent, f"{gs.path.stem}_repr{gs.path.suffix}")

    out_srs = osr.SpatialReference()
    out_srs.SetFromUserInput(crs)
    out_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    dst_src = gdal.Warp(str(fname_int), gs.src, dstSRS=out_srs)
    tr_src = gdal.Translate(str(fname), dst_src)

    out_srs = None
    tr_src = None
    dst_src = None
    gs.close()
    gc.collect()

    os.remove(fname_int)

    return open_grid(fname)
