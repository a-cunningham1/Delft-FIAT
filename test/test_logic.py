from delft_fiat.models.calc import calc_rp_coef, calc_risk

import pytest


def test_calc_risk():
    rps = [1, 2, 5, 25, 50, 100]
    dms = [5, 10, 50, 300, 1200, 3000]

    coef = calc_rp_coef(rps)
    ead = calc_risk(coef, dms)

    assert ead == 98.49343647185707


def test_calc_risk_one():
    rps = [10]
    dms = [5]

    coef = calc_rp_coef(rps)
    ead = calc_risk(coef, dms)

    assert ead == 0.5
