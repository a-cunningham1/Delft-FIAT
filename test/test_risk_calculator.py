from delft_fiat.models.calc import risk_calculator

def test_risk_calculator():
    rps = [1, 2, 5, 25, 50, 100]
    damages = [5, 10, 50, 300, 1200, 3000]

    ead = risk_calculator(return_periods=rps, damages=damages)

    assert ead == 98.49343647185707


def test_risk_calculator_one_rp():
    rps = [10]
    damages = [5]

    ead = risk_calculator(return_periods=rps, damages=damages)

    assert ead == 0.5