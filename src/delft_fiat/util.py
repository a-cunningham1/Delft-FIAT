import sys
from ast import literal_eval
from gc import get_referents
from enum import Enum
from pathlib import Path
from types import ModuleType, FunctionType

BLACKLIST = type, ModuleType, FunctionType

_GeomDriverTable = {
    ".geojson": "GeoJSON",
    ".nc": "netCDF",
    ".shp": "ESRI Shapfile",
}

_GridDriverTable = {
    ".nc": "netCDF",
    ".tif": "GTiff",
    ".vrt": "VRT",
}


def _detertype(elem):
    """_summary_"""

    try:
        dt = type(literal_eval(elem))
        return dt
    except Exception:
        return str


def ObjectSize(obj):
    """Actual size of an object (bit overestimated)
    Thanks to this post on stackoverflow:
    (https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python)

    Just for internal and debugging uses
    """
    if isinstance(obj, BLACKLIST):
        raise TypeError("getsize() does not take argument of type: " + str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size


def GenericPathCheck(
    path: str,
    root: str,
) -> Path:
    """_summary_

    Parameters
    ----------
    path : str
        _description_
    root : str
        _description_

    Returns
    -------
    Path
        _description_

    Raises
    ------
    FileNotFoundError
        _description_
    """

    path = Path(path)
    if not path.is_absolute():
        path = Path(root, path)
    if not (not path.is_file() or not path.is_dir()):
        raise FileNotFoundError(f"{str(path)} is not a valid path")
    return path
