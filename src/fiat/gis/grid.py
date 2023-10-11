"""Only raster methods for FIAT."""

import gc
import os
from pathlib import Path

from osgeo import gdal, osr

from fiat.io import open_grid


def clip(
    band: gdal.Band,
    gtf: tuple,
    idx: tuple,
):
    """_summary_.

    Parameters
    ----------
    band : gdal.Band
        _description_
    gtf : tuple
        _description_
    idx : tuple
        _description_
    """
    pass


def reproject(
    gs: object,
    crs: str,
    out: str = None,
    resample: int = 0,
) -> object:
    """_summary_.

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
    _gs_kwargs = gs._kwargs

    if not Path(str(out)).is_dir():
        out = gs.path.parent

    fname_int = Path(out, f"{gs.path.stem}_repr_fiat.tif")
    fname = Path(out, f"{gs.path.stem}_repr_fiat{gs.path.suffix}")

    out_srs = osr.SpatialReference()
    out_srs.SetFromUserInput(crs)
    out_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    dst_src = gdal.Warp(
        str(fname_int),
        gs.src,
        dstSRS=out_srs,
        resampleAlg=resample,
    )

    out_srs = None

    if gs.path.suffix == ".tif":
        gs.close()
        dst_src = None
        return open_grid(fname_int)

    gs.close()
    gdal.Translate(str(fname), dst_src)
    dst_src = None
    gc.collect()

    os.remove(fname_int)

    return open_grid(fname, **_gs_kwargs)