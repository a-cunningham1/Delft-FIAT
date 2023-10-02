def world2pixel(geoMatrix, x, y):
    """Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate

    (Thanks to the ogr cookbook!;
    https://pcjericks.github.io/py-gdalogr-cookbook/index.html)
    """

    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    #   yDist = geoMatrix[5]
    #   rtnX = geoMatrix[2]
    #   rtnY = geoMatrix[4]
    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / xDist)
    return (pixel, line)


def pixel2world(geoMatrix, x, y):
    """_Summary_"""

    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    coorX = ulX + (x * xDist)
    coorY = ulY + (y * yDist)
    return (coorX, coorY)
