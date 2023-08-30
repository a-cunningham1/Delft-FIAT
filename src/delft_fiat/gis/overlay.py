from delft_fiat.gis.util import world2pixel, pixel2world
from delft_fiat.io import Grid

from osgeo import gdal, ogr


def clip(
    band: Grid,
    srs: "osr.SpatialReference",
    gtf: tuple,
    ft: ogr.Feature,
) -> "numpy.array":
    """_summary_

    Parameters
    ----------
    src : gdal.Dataset
        _description_
    band : gdal.Band
        _description_
    ft : ogr.Feature
        _description_

    Returns
    -------
    numpy.array
        _description_
    """

    geom = ft.GetGeometryRef()

    minX, maxX, minY, maxY = geom.GetEnvelope()
    ulX, ulY = world2pixel(gtf, minX, maxY)
    lrX, lrY = world2pixel(gtf, maxX, minY)
    c = pixel2world(gtf, ulX, ulY)
    new_gtf = (c[0], gtf[1], 0.0, c[1], 0.0, gtf[-1])
    pxWidth = int(lrX - ulX) + 1
    pxHeight = int(lrY - ulY) + 1

    clip = band[ulX, ulY, pxWidth, pxHeight]
    # m = mask.ReadAsArray(ulX,ulY,pxWidth,pxHeight)

    # pts = geom.GetGeometryRef(0)
    # pixels = [None] * pts.GetPointCount()
    # for p in range(pts.GetPointCount()):
    #     pixels[p] = (world2Pixel(gtf, pts.GetX(p), pts.GetY(p)))

    dr_r = gdal.GetDriverByName("MEM")
    b_r = dr_r.Create("memset", pxWidth, pxHeight, 1, gdal.GDT_Int16)
    b_r.SetSpatialRef(srs)
    b_r.SetGeoTransform(new_gtf)

    dr_g = ogr.GetDriverByName("Memory")
    src_g = dr_g.CreateDataSource("memdata")
    lay_g = src_g.CreateLayer("mem", srs)
    lay_g.CreateFeature(ft)

    gdal.RasterizeLayer(b_r, [1], lay_g, None, None, [1], ["ALL_TOUCHED=TRUE"])
    clip = clip[b_r.ReadAsArray() == 1]

    b_r = None
    dr_r = None
    lay_g = None
    src_g = None
    dr_g = None

    return clip


def clip_weighted(
    band: gdal.Band,
    srs: "osr.SpatialReference",
    gtf: tuple,
    ft: ogr.Feature,
    upscale: int = 1,
) -> "numpy.array":
    """_summary_

    Parameters
    ----------
    src : gdal.Dataset
        _description_
    band : gdal.Band
        _description_
    ft : ogr.Feature
        _description_

    Returns
    -------
    numpy.array
        _description_
    """

    geom = ft.GetGeometryRef()

    minX, maxX, minY, maxY = geom.GetEnvelope()
    ulX, ulY = world2pixel(gtf, minX, maxY)
    lrX, lrY = world2pixel(gtf, maxX, minY)
    c = pixel2world(gtf, ulX, ulY)
    new_gtf = (c[0], gtf[1] / upscale, 0.0, c[1], 0.0, gtf[-1] / upscale)
    pxWidth = int(lrX - ulX) + 1
    pxHeight = int(lrY - ulY) + 1

    clip = band.ReadAsArray(ulX, ulY, pxWidth, pxHeight)
    # m = mask.ReadAsArray(ulX,ulY,pxWidth,pxHeight)

    # pts = geom.GetGeometryRef(0)
    # pixels = [None] * pts.GetPointCount()
    # for p in range(pts.GetPointCount()):
    #     pixels[p] = (world2Pixel(gtf, pts.GetX(p), pts.GetY(p)))

    dr_r = gdal.GetDriverByName("MEM")
    b_r = dr_r.Create(
        "memset", pxWidth * upscale, pxHeight * upscale, 1, gdal.GDT_Int16
    )
    b_r.SetSpatialRef(srs)
    b_r.SetGeoTransform(new_gtf)

    dr_g = ogr.GetDriverByName("Memory")
    src_g = dr_g.CreateDataSource("memdata")
    lay_g = src_g.CreateLayer("mem", srs)
    lay_g.CreateFeature(ft)

    gdal.RasterizeLayer(b_r, [1], lay_g, None, None, [1], ["ALL_TOUCHED=TRUE"])
    _w = b_r.ReadAsArray().reshape((pxHeight, upscale, pxWidth, -1)).mean(3).mean(1)
    clip = clip[_w != 0]

    b_r = None
    dr_r = None
    lay_g = None
    src_g = None
    dr_g = None

    return clip, _w


def mask(
    driver: str,
):
    pass


def pin(
    band: Grid,
    gtf: tuple,
    point: tuple,
) -> "numpy.array":
    """_summary_

    Parameters
    ----------
    src : gdal.Band
        _description_
    band : gdal.Band
        _description_
    point : tuple
        _description_

    Returns
    -------
    numpy.array
        _description_
    """

    X, Y = world2pixel(gtf, *point)

    value = band[X, Y, 1, 1]

    return value[0]
