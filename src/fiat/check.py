from fiat.log import spawn_logger, setup_default_log
from fiat.util import NEWLINE_CHAR, deter_type, generic_path_check

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


def check_geom_extent(
    gm_bounds: tuple | list,
    gr_bounds: tuple | list,
):
    """_summary_"""

    _checks = (
        gm_bounds[0] > gr_bounds[0],
        gm_bounds[1] < gr_bounds[1],
        gm_bounds[2] > gr_bounds[2],
        gm_bounds[3] < gr_bounds[3],
    )

    if not all(_checks):
        logger.error(f"Geometry bounds {gm_bounds} exceed hazard bounds {gr_bounds}")
        sys.exit()


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


## Vulnerability
