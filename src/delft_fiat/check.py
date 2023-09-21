from delft_fiat.log import spawn_logger, setup_default_log
from delft_fiat.util import NEWLINE_CHAR, deter_type, generic_path_check

import fnmatch
import sys
from osgeo import gdal
from osgeo import osr
from pathlib import Path

logger = spawn_logger("fiat.checks")


## Config
def check_config_entries(
    keys: tuple,
    path: Path,
    parent: Path,
):
    """_summary_"""

    _man_cols = [
        "output.path",
        "hazard.file",
        "hazard.risk",
        "hazard.elevation_reference",
        "vulnerability.file",
    ]

    _check = [item in keys for item in _man_cols]
    if not all(_check):
        error_log = setup_default_log(
            "error",
            log_level=2,
            dst=str(parent),
        )
        _missing = [item for item, b in zip(_man_cols, _check) if not b]
        error_log.error(f"Missing mandatory entries in '{path.name}'")
        error_log.info(f"Please fill in the following missing entries: {_missing}")
        sys.exit()


def check_config_geom(
    cfg: "ConfigReader",
):
    """_summary_"""

    _req_cols = [
        "exposure.geom.crs",
        "exposure.geom.csv",
        "exposure.geom.file1",
    ]
    _all_geom = [item for item in cfg if item.startswith("exposure.geom")]
    if len(_all_geom) == 0:
        return False

    _check = [item in _all_geom for item in _req_cols]
    if not all(_check):
        _missing = [item for item, b in zip(_req_cols, _check) if not b]
        logger.warning(
            f"Info for the geometry model was found, but not all. {_missing} was/ were missing"
        )
        return False

    return True


def check_config_grid(
    cfg: "ConfigReader",
):
    """_summary_"""

    _req_cols = [
        "exposure.grid.crs",
        "exposure.grid.file",
    ]
    _all_grid = [item for item in cfg if item.startswith("exposure.grid")]
    if len(_all_grid) == 0:
        return False

    _check = [item in _all_grid for item in _req_cols]
    if not all(_check):
        _missing = [item for item, b in zip(_req_cols, _check) if not b]
        logger.warning(
            f"Info for the grid (raster) model was found, but not all. {_missing} was/ were missing"
        )
        return False

    return True


def check_global_crs(
    srs: osr.SpatialReference,
    fname: str,
    fname_haz: str,
):
    """_summary_"""

    if srs is None:
        logger.error("Could not infer the srs from '{}', nor from '{}'")
        logger.dead("Exiting...")
        sys.exit()


## GIS
def check_grid_exact(
    haz,
    exp,
):
    """_summary_"""

    if not check_vs_srs(
        haz.get_srs(),
        exp.get_srs(),
    ):
        logger.error("")
        sys.exit()

    gtf1 = [round(_n, 2) for _n in haz.get_geotransform()]
    gtf2 = [round(_n, 2) for _n in exp.get_geotransform()]

    if gtf1 != gtf2:
        logger.error()
        sys.exit()

    if haz.shape != exp.shape:
        logger.error("")
        sys.exit()


def check_internal_srs(
    source_srs: osr.SpatialReference,
    fname: str,
    cfg_srs: osr.SpatialReference = None,
):
    """_summary_"""

    if source_srs is None and cfg_srs is None:
        logger.error(
            f"Coordinate reference system is unknown for '{fname}', cannot safely continue"
        )
        logger.dead("Exiting...")
        sys.exit()

    if source_srs is None:
        source_srs = osr.SpatialReference()
        source_srs.SetFromUserInput(cfg_srs)
        return source_srs

    return None


def check_vs_srs(
    global_srs: osr.SpatialReference,
    source_srs: osr.SpatialReference,
):
    """_summary_"""

    if not (
        global_srs.IsSame(source_srs)
        or global_srs.ExportToProj4() == source_srs.ExportToProj4()
    ):
        return False

    return True


## Hazard
def check_hazard_band_names(
    bnames: list,
    risk: bool,
    rp: list,
    count: int,
):
    """_summary_"""

    if risk:
        return [f"{n}Y" for n in rp]

    if count == 1:
        return [""]

    return bnames


def check_hazard_rp_iden(
    bnames: list,
    rp_cfg: list,
    path: Path,
):
    """_summary_"""
    l = len(bnames)

    bn_str = "\n".join(bnames).encode()
    if deter_type(bn_str, l - 1) != 3:
        return [float(n) for n in bnames]

    if len(rp_cfg) == len(bnames):
        rp_str = "\n".join([str(n) for n in rp_cfg]).encode()
        if deter_type(rp_str, l - 1) != 3:
            return rp_cfg

    logger.error(
        f"'{path.name}': cannot determine the return periods for the risk calculation"
    )
    logger.error(
        f"Names of the bands are: {bnames}, \
return periods in settings toml are: {rp_cfg}"
    )
    logger.info("Specify either one them correctly")
    sys.exit()


def check_hazard_subsets(
    sub: dict,
    path: Path,
):
    """_summary_"""

    if sub is not None:
        keys = ", ".join(list(sub.keys()))
        logger.error(
            f"""'{path.name}': cannot read this file as there are \
multiple datasets (subsets)"""
        )
        logger.info(f"Chose one of the following subsets: {keys}")
        sys.exit()


## Exposure
def check_exp_columns(
    columns: tuple | list,
):
    """_summary_"""

    _man_columns = [
        "Object ID",
        "Ground Elevation",
        "Ground Floor Height",
    ]

    _check = [item in columns for item in _man_columns]
    if not all(_check):
        _missing = [item for item, b in zip(_man_columns, _check) if not b]
        logger.error(f"Missing mandatory exposure columns: {_missing}")
        sys.exit()

    dmg = fnmatch.filter(columns, "Damage Function: *")
    dmg_suffix = [item.split(":")[1].strip() for item in dmg]
    mpd = fnmatch.filter(columns, "Max Potential Damage: *")
    mpd_suffix = [item.split(":")[1].strip() for item in mpd]

    if not dmg:
        logger.error("No damage function were given in ")
        sys.exit()

    if not mpd:
        logger.error("No maximum potential damages were given in ")
        sys.exit()

    _check = [item in mpd_suffix for item in dmg_suffix]
    if not any(_check):
        logger.error("Damage function and maximum potential damage do not have a single match")
        sys.exit()
    if not all(_check):
        _missing = [item for item, b in zip(dmg_suffix, _check) if not b]
        logger.warning(f"No every damage function has a corresponding maximum potential damage: {_missing}")

## Vulnerability
