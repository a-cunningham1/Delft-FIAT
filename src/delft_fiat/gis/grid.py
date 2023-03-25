from osgeo import gdal, osr


def reproject(
    gs: "GridSource",
    crs: str,
) -> object:
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)
    tx = osr.CoordinateTransformation(wgs84, osng)

    g = gdal.Open(dataset)

    geo_t = g.GetGeoTransform()
    x_size = g.RasterXSize
    y_size = g.RasterYSize

    (ulx, uly, ulz) = tx.TransformPoint(geo_t[0], geo_t[3])
    (lrx, lry, lrz) = tx.TransformPoint(
        geo_t[0] + geo_t[1] * x_size, geo_t[3] + geo_t[5] * y_size
    )

    mem_drv = gdal.GetDriverByName("MEM")

    dest = mem_drv.Create(
        "",
        int((lrx - ulx) / pixel_spacing),
        int((uly - lry) / pixel_spacing),
        1,
        gdal.GDT_Float32,
    )

    new_geo = (ulx, pixel_spacing, geo_t[2], uly, geo_t[4], -pixel_spacing)

    dest.SetGeoTransform(new_geo)
    dest.SetProjection(osng.ExportToWkt())

    res = gdal.ReprojectImage(
        g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear
    )
    return dest

    pass


if __name__ == "__main__":
    pass
