from delft_fiat.io import open_csv
from delft_fiat.models import GeomModel

import pytest
from pathlib import Path


def test_geom_model(tmpdir, cfg_event):
    cfg_event.set_output_dir(str(tmpdir))
    model = GeomModel(cfg_event)
    model.run()

    # check the output
    out = open_csv(Path(str(tmpdir), "output.csv"), index="Object ID")
    assert float(out[2, "Total Damage"]) == 740
    assert float(out[3, "Total Damage"]) == 1038


def test_raster_model():
    pass
