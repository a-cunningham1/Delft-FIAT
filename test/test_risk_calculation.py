from delft_fiat.models import GeomModel

import pytest


def test_risk_calculation(tmpdir, cfg):
    model = GeomModel(cfg)
    model.run()