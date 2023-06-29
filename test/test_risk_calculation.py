from delft_fiat.models import GeomModel

import pytest


def test_risk_calculation(tmpdir, cfg_risk):
    model = GeomModel(cfg_risk)
    model.run()