from delft_fiat.io import open_geom

import gc
from osgeo import ogr
from osgeo import osr
from pathlib import Path


def coor_transform():
    pass


def geom_centroid(ft: ogr.Feature) -> tuple:
    """_summary_"""

    pass


def point_in_geom(
    ft: ogr.Feature,
) -> tuple:
    """_Summary_"""

    geom = ft.GetGeometryRef()
    p = geom.PointOnSurface()
    geom = None
    return p.GetX(), p.GetY()


def reproject_feature(
    ft: ogr.Feature,
    crs: str,
):
    pass


def reproject(
    gs: "GeomSource",
    crs: str,
) -> object:
    out_srs = osr.SpatialReference()
    out_srs.SetFromUserInput(crs)
    out_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    transform = osr.CoordinateTransformation(
        gs.get_srs(),
        out_srs,
    )

    mem_gs = open_geom(
        file="memset",
        driver="Memory",
        mode="w",
    )

    mem_gs.create_layer(
        out_srs,
        gs.layer.GetGeomType(),
    )
    mem_gs.set_layer_from_defn(
        gs.layer.GetLayerDefn(),
    )

    for ft in gs.layer:
        geom = ft.GetGeometryRef()
        geom.Transform(transform)

        ft.SetGeometry(geom)
        mem_gs.layer.CreateFeature(ft)

    geom = None
    ft = None
    out_srs = None
    transform = None

    fname = Path(gs.path.parent, f"{gs.path.stem}_repr{gs.path.suffix}")
    with open_geom(fname, gs._driver.GetName(), mode="w") as new_gs:
        new_gs.create_layer_from_copy(mem_gs.layer)

    mem_gs.close()
    del mem_gs
    gc.collect()

    return new_gs.reopen()


if __name__ == "__main__":
    from delft_fiat.cfg import ConfigReader

    c = ConfigReader(r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\Casus\settings.toml")

    a = open_geom(c.get_path("exposure", "geom_file"), mode="r")
    import time

    s = time.time()
    gs = reproject(a, "EPSG:4326")
    e = time.time() - s
    print(f"{e} seconds!")
    pass
