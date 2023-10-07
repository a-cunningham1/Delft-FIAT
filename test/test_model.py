from fiat.io import open_csv
from fiat.models import GeomModel

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


def test_geom_missing(tmpdir, mis_event):
    mis_event.set_output_dir(str(tmpdir))
    model = GeomModel(mis_event)
    model.run()

    assert Path(str(tmpdir), "missing.log").exists()
    missing = open(Path(str(tmpdir), "missing.log"), "r")
    assert sum(1 for _ in missing) == 1


def test_raster_model():
    pass
