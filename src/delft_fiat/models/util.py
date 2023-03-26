from delft_fiat.util import GenericPathCheck

import re
from pathlib import Path


def DamageLookup(
    csv: str,
    oid: str,
    root: str,
):
    f = open(csv, "r")
    ncol = len(f.readline().split(","))
    r = re.compile(f"{oid}" + ".+" * (ncol - 1))
    m = r.findall(f.read())
    if not m:
        raise FileNotFoundError(f"{oid}")
    else:
        oid, path, method = m[0].split(",")
        path = GenericPathCheck(path, root)
        return path, method


if __name__ == "__main__":
    DamageLookup(
        r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\damage_curves.csv",
        "h_struct_501",
    )
    pass
