import os
import sys
from ast import literal_eval
from gc import get_referents
from enum import Enum
from pathlib import Path
from types import ModuleType, FunctionType

BLACKLIST = type, ModuleType, FunctionType

_GeomDriverTable = {
    "": "Memory",
    ".csv": "CSV",
    ".gdb": "FileGDB",
    ".geojson": "GeoJSON",
    ".gpkg": "GPKG",
    ".nc": "netCDF",
    ".shp": "ESRI Shapefile",
}

_GridDriverTable = {
    "": "MEM",
    ".nc": "netCDF",
    ".tif": "GTiff",
    ".vrt": "VRT",
}


def replace_empty(l):
    """_summary_"""

    return ["nan" if not e else e.decode() for e in l]


def deter_type(elem):
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


def generic_folder_check(
    path: str,
):
    """_summary_

    Parameters
    ----------
    path : str
        _description_
    """

    path = Path(path)
    if not path.exists():
        os.makedirs(path)


def generic_path_check(
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
    if not (path.is_file() | path.is_dir()):
        raise FileNotFoundError(f"{str(path)} is not a valid path")
    return path
