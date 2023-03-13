from osgeo import ogr


def GeomCentroid(ft: ogr.Feature):
    pass


def Reproject(ft: ogr.Feature):
    pass


if __name__ == "__main__":
    d = ogr.GetDriverByName("ESRI Shapefile")
    e = d.Open(
        r"c:\CODING\PYTHON_DEV\Delft_FIAT\tmp\Database\Exposure\C8\C8_Spatial.shp"
    )
    l = e.GetLayer()
    ld = l.GetLayerDefn()
    pass
