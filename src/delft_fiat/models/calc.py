from delft_fiat.gis import overlay


def calculate_coefficients(T):
    """Calculates coefficients used to compute the EAD as a linear function of the known damages
    Args:
        T (list of ints): return periods T1 … Tn for which damages are known
    Returns:
        alpha [list of floats]: coefficients a1, …, an (used to compute the AED as a linear function of the known damages)
    In which D(f) is the damage, D, as a function of the frequency of exceedance, f. In order to compute this EAD,
    function D(f) needs to be known for the entire range of frequencies. Instead, D(f) is only given for the n
    frequencies as mentioned in the table above. So, in order to compute the integral above, some assumptions need
    to be made for function D(h):
    (i)	   For f > f1 the damage is assumed to be equal to 0
    (ii)   For f<fn, the damage is assumed to be equal to Dn
    (iii)  For all other frequencies, the damage is estimated from log-linear interpolation between the known damages and frequencies
    """
    # Step 1: Compute frequencies associated with T-values.
    f = [1 / i for i in T]
    lf = [np.log(1 / i) for i in T]

    # Step 2:
    c = [(1 / (lf[i] - lf[i + 1])) for i in range(len(T[:-1]))]

    # Step 3:
    G = [(f[i] * lf[i] - f[i]) for i in range(len(T))]

    # Step 4:
    a = [
        ((1 + c[i] * lf[i + 1]) * (f[i] - f[i + 1]) + c[i] * (G[i + 1] - G[i]))
        for i in range(len(T[:-1]))
    ]
    b = [
        (c[i] * (G[i] - G[i + 1] + lf[i + 1] * (f[i + 1] - f[i])))
        for i in range(len(T[:-1]))
    ]

    # Step 5:
    if len(T) == 1:
        alpha = f
    else:
        alpha = [
            b[0] if i == 0 else f[i] + a[i - 1] if i == len(T) - 1 else a[i - 1] + b[i]
            for i in range(len(T))
        ]
    return alpha


def damage_factor(inun, gr_lvl, method=None):
    return inun.mean()


def damage_calculator():
    _func = {}

    pass


def inundation_depth(
    h: "numpy.array",
    ref: str,
    dem: float,
    gfh: float,
):
    """_summary_

    Parameters
    ----------
    h : numpy.array
        _description_
    ref : str
        _description_
    dem : float
        _description_
    gfh : float
        _description_

    Returns
    -------
    _type_
        _description_
    """

    if ref == "DEM":
        return h.mean()

    elif ref == "DATUM":
        return


def risk_calculator():
    pass
