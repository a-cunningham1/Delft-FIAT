from delft_fiat.models import GeomModel

import pytest


def test_geom_model(tmpdir, cfg):
    model = GeomModel(cfg)
    model.run()


def test_raster_model():
    pass
