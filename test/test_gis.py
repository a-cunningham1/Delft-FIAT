from fiat.gis import overlay, geom, grid

from numpy import mean


def test_clip_grid_geom(gm, gr_event):
    for ft in gm:
        hazard = overlay.clip(
            gr_event[1],
            gr_event.get_srs(),
            gr_event.get_geotransform(),
            ft,
        )

    assert len(hazard) == 7
    assert int(round(mean(hazard) * 100, 0)) == 166


def test_pin(gm, gr_event):
    for ft in gm:
        XY = geom.point_in_geom(ft)

        hazard = overlay.pin(
            gr_event[1],
            gr_event.get_geotransform(),
            XY,
        )

    assert int(round(hazard[0] * 100, 0)) == 160


def test_reproject(tmpdir, gm, gr_event):
    dst_crs = "EPSG:3857"

    new_gm = geom.reproject(
        gm,
        dst_crs,
        str(tmpdir),
    )

    new_gr = grid.reproject(
        gr_event,
        dst_crs,
        str(tmpdir),
    )

    assert new_gm.get_srs().GetAuthorityCode(None) == "3857"
    assert new_gr.get_srs().GetAuthorityCode(None) == "3857"
