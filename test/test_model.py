from delft_fiat.models import GeomModel

import pytest


def test_geom_model(tmpdir, cfg_event):
    model = GeomModel(cfg_event)
    model.run()


def test_raster_model():
    pass
