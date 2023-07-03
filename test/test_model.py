from delft_fiat.models import GeomModel

import pytest
from pathlib import Path


def test_geom_model(tmpdir, cfg_event):
    cfg_event.set_output_dir(str(tmpdir))
    model = GeomModel(cfg_event)
    model.run()


def test_raster_model():
    pass
