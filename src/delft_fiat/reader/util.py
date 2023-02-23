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
        raise FileNotFoundError(f"File: {str(path)} is not a valid path to a file")


def DamageLookup(
    f: str,
    oid: str,
):
    f = open(f, "r")
    ncol = len(f.readline().split(","))
    r = re.compile(f"{oid}" + ".+" * (ncol - 1))
    m = r.findall(f.read())
    if not m:
        print("Blyat")
        return
    else:
        return m[0]


if __name__ == "__main__":
    DamageLookup(
        r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\damage.csv",
        "h_struct_501",
    )
    pass
