import re
from pathlib import Path


def GenericFileCheck(
    path: str,
    root: str,
):
    path = Path(path)
    if not path.is_absolute():
        path = Path(root, path)
    if not path.is_file():
        raise FileNotFoundError(f"{str(path)} is not a valid path")
    return path


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
        return None
    else:
        oid, path, method = m[0].split(",")
        path = GenericFileCheck(path, root)
        return path, method


if __name__ == "__main__":
    DamageLookup(
        r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\damage_curves.csv",
        "h_struct_501",
    )
    pass
