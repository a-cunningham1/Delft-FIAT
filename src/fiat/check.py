"""Checks for the data of FIAT."""

from pathlib import Path

from osgeo import osr

from fiat.error import FIATDataError
from fiat.gis.crs import get_srs_repr
from fiat.log import spawn_logger
from fiat.util import deter_type

logger = spawn_logger("fiat.checks")


## Config
def check_config_entries(
    keys: tuple,
    path: Path,
    extra_entries: list,
):
    """_summary_."""
    _man_entries = [
        "output.path",
        "hazard.file",
        "hazard.risk",
        "vulnerability.file",
    ] + extra_entries

    _check = [item in keys for item in _man_entries]
    if not all(_check):
        _missing = [item for item, b in zip(_man_entries, _check) if not b]
        msg = f"Missing mandatory entries in '{path.name}'. Please fill in the \
following missing entries: {_missing}"
        raise FIATDataError(msg)


def check_config_geom(
    cfg: object,
):
    """_summary_."""
    _req_fields = [
        "exposure.geom.crs",
        "exposure.geom.file1",
    ]
    _all_geom = [
        item for item in cfg if item.startswith(("exposure.geom", "exposure.csv"))
    ]
    if len(_all_geom) == 0:
        return False

    _check = [item in _all_geom for item in _req_fields]
    if not all(_check):
        _missing = [item for item, b in zip(_req_fields, _check) if not b]
        logger.warning(
            f"Info for the geometry model was found, but not all. \
{_missing} was/ were missing"
        )
        return False

    return True


def check_config_grid(
    cfg: object,
):
    """_summary_."""
    _req_fields = [
        "exposure.grid.crs",
        "exposure.grid.file",
    ]
    _all_grid = [item for item in cfg if item.startswith("exposure.grid")]
    if len(_all_grid) == 0:
        return False

    _check = [item in _all_grid for item in _req_fields]
    if not all(_check):
        _missing = [item for item, b in zip(_req_fields, _check) if not b]
        logger.warning(
            f"Info for the grid (raster) model was found, but not all. \
{_missing} was/ were missing"
        )
        return False

    return True


def check_global_crs(
    srs: osr.SpatialReference,
    fname: str,
    fname_haz: str,
):
    """_summary_."""
    if srs is None:
        msg = "Could not infer the srs from '{}', nor from '{}'"
        raise FIATDataError(msg)


## Text files
def check_duplicate_columns(
    cols,
):
    """_summary_."""
    if cols is not None:
        msg = f"Duplicate columns were encountered. Wrong column could \
be used. Check input for these columns: {cols}"
        raise FIATDataError(msg)


## GIS
########################### Print clipped exposure data: If exposure input is beyond the hazard extent it is clipped
# def clip_exposure_to_hazard(hazard_ds, exposure_ds, output_path="clipped_exposure.tif"):
#     """
#     Clips the exposure grid to match the hazard grid extent.
#
#     Args:
#         hazard_ds (gdal.Dataset): Hazard dataset.
#         exposure_ds (gdal.Dataset): Exposure dataset.
#         output_path (str): Path to save the clipped exposure grid.
#
#     Returns:
#         gdal.Dataset: Clipped exposure dataset.
#     """
#     if not isinstance(hazard_ds, gdal.Dataset):
#         raise ValueError("Hazard grid is not a valid GDAL Dataset.")
#     if not isinstance(exposure_ds, gdal.Dataset):
#         raise ValueError("Exposure grid is not a valid GDAL Dataset.")
#
#     # Extract the extent and geotransform of the hazard dataset
#     hazard_gt = hazard_ds.GetGeoTransform()
#     hazard_x_min = hazard_gt[0]
#     hazard_y_max = hazard_gt[3]
#     hazard_x_max = hazard_x_min + hazard_gt[1] * hazard_ds.RasterXSize
#     hazard_y_min = hazard_y_max + hazard_gt[5] * hazard_ds.RasterYSize
#
#     hazard_extent = (hazard_x_min, hazard_y_min, hazard_x_max, hazard_y_max)
#
#     logger.info(f"Hazard extent: {hazard_extent}")
#     if hazard_extent[0] >= hazard_extent[2] or hazard_extent[1] >= hazard_extent[3]:
#         raise RuntimeError(f"Invalid hazard extent: {hazard_extent}")
#
#     # Define GDAL warp options for clipping
#     warp_options = gdal.WarpOptions(
#         format="GTiff",
#         outputBounds=hazard_extent,
#         xRes=hazard_gt[1],
#         yRes=abs(hazard_gt[5]),
#         dstSRS=hazard_ds.GetProjection(),
#         resampleAlg="nearest"
#     )
#
#     logger.info("Clipping exposure grid to match the hazard grid extent.")
#
#     # Perform the warp
#     gdal.Warp(output_path, exposure_ds, options=warp_options)
#
#     # Open the saved clipped dataset
#     clipped_exposure_ds = gdal.Open(output_path)
#     if clipped_exposure_ds is None:
#         logger.error("gdal.Warp failed to produce a valid clipped dataset.")
#         raise RuntimeError("Failed to clip the exposure grid to the hazard grid extent.")
#
#     logger.info(f"Clipped exposure grid saved to: {output_path}")
#
#     return clipped_exposure_ds

#######################################################
##### New check_grid_exact function that checks if exposure grid is larger than the hazard grid
# def check_grid_exact(haz, exp):
#     """
#     Ensure the exposure grid matches the hazard grid in extent and CRS.
#
#     Args:
#         haz (fiat.io.GridSource or gdal.Dataset): Hazard grid dataset.
#         exp (fiat.io.GridSource or gdal.Dataset): Exposure grid dataset.
#
#     Returns:
#         tuple: Updated hazard and exposure grids as GDAL Datasets.
#     """
#     # Extract GDAL Dataset from GridSource if needed
#     def to_gdal_dataset(grid):
#         if isinstance(grid, gdal.Dataset):
#             return grid
#         elif hasattr(grid, "src") and isinstance(grid.src, gdal.Dataset):
#             logger.info("Using 'src' attribute to extract GDAL Dataset.")
#             return grid.src
#         elif hasattr(grid, "path"):
#             logger.info(f"Opening dataset from path: {grid.path}")
#             dataset = gdal.Open(grid.path)
#             if dataset is not None:
#                 return dataset
#         raise ValueError(f"Unable to extract GDAL Dataset from: {type(grid)}")
#
#     # Convert hazard and exposure grids to GDAL datasets
#     haz = to_gdal_dataset(haz)
#     exp = to_gdal_dataset(exp)
#
#     # Check CRS compatibility
#     if haz.GetProjection() != exp.GetProjection():
#         logger.error("Spatial reference systems (CRS) do not match.")
#         sys.exit(1)
#
#     # Get dimensions
#     haz_shape = (haz.RasterYSize, haz.RasterXSize)
#     exp_shape = (exp.RasterYSize, exp.RasterXSize)
#
#     logger.info(f"Hazard grid shape: {haz_shape}")
#     logger.info(f"Exposure grid shape: {exp_shape}")
#
#     # Clip exposure grid if it's larger than the hazard grid
#     if exp_shape[0] > haz_shape[0] or exp_shape[1] > haz_shape[1]:
#         logger.warning("Exposure grid is larger than the hazard grid. Clipping it.")
#         exp = clip_exposure_to_hazard(haz, exp)
#
#     # Check if exposure grid is smaller than the hazard grid
#     if exp_shape[0] < haz_shape[0] or exp_shape[1] < haz_shape[1]:
#         logger.warning("Exposure grid is smaller than the hazard grid. No clipping performed.")
#
#     return haz, exp






###########################
def check_grid_exact(
    haz,
    exp,
):
    """_summary_."""
    if not check_vs_srs(
        haz.get_srs(),
        exp.get_srs(),
    ):
        msg = f"CRS of hazard data ({get_srs_repr(haz.get_srs())}) does not match the \
CRS of the exposure data ({get_srs_repr(exp.get_srs())})"
        logger.warning(msg)
        return False

    gtf1 = [round(_n, 2) for _n in haz.get_geotransform()]
    gtf2 = [round(_n, 2) for _n in exp.get_geotransform()]

    if gtf1 != gtf2:
        msg = f"Geotransform of hazard data ({gtf1}) does not match geotransform of \
exposure data ({gtf2})"
        logger.warning(msg)
        return False

    if haz.shape != exp.shape:
        msg = f"Shape of hazard ({haz.shape}) does not match shape of \
exposure data ({exp.shape})"
        logger.warning(msg)
        return False

    return True


def check_internal_srs(
    source_srs: osr.SpatialReference,
    fname: str,
    cfg_srs: str = None,
):
    """_summary_."""
    if source_srs is None and cfg_srs is None:
        msg = f"Coordinate reference system is unknown for '{fname}', \
cannot safely continue"
        raise FIATDataError(msg)

    if source_srs is None:
        source_srs = osr.SpatialReference()
        source_srs.SetFromUserInput(cfg_srs)
        return source_srs

    return None


def check_geom_extent(
    gm_bounds: tuple | list,
    gr_bounds: tuple | list,
):
    """_summary_."""
    _checks = (
        gm_bounds[0] > gr_bounds[0],
        gm_bounds[1] < gr_bounds[1],
        gm_bounds[2] > gr_bounds[2],
        gm_bounds[3] < gr_bounds[3],
    )

    if not all(_checks):
        msg = f"Geometry bounds {gm_bounds} exceed hazard bounds {gr_bounds}"
        raise FIATDataError(msg)


def check_vs_srs(
    global_srs: osr.SpatialReference,
    source_srs: osr.SpatialReference,
):
    """_summary_."""
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
    """_summary_."""
    if risk:
        return [f"{n}y" for n in rp]

    if count == 1:
        return [""]

    return bnames


def check_hazard_rp(
    rp_bands: list,
    rp_cfg: list,
    path: Path,
):
    """_summary_."""
    l = len(rp_bands)

    bn_str = "\n".join(rp_bands).encode()
    if deter_type(bn_str, l - 1) != 3:
        return [float(n) for n in rp_bands]

    if rp_cfg is not None:
        if len(rp_cfg) == len(rp_bands):
            rp_str = "\n".join([str(n) for n in rp_cfg]).encode()
            if deter_type(rp_str, l - 1) != 3:
                return [float(n) for n in rp_cfg]

    msg = f"'{path.name}': cannot determine the return periods for \
the risk calculation. Return periods specified with the bands are: {rp_bands}, \
return periods in settings toml are: {rp_cfg}"
    raise FIATDataError(msg)


def check_hazard_subsets(
    sub: dict,
    path: Path,
):
    """_summary_."""
    if sub is not None:
        keys = ", ".join(list(sub.keys()))
        msg = f"'{path.name}': cannot read this file as there are \
multiple datasets (subsets). Chose one of the following subsets: {keys}"
        raise FIATDataError(msg)


## Exposure
def check_exp_columns(
    index_col: str,
    columns: tuple | list,
    specific_columns: tuple | list = [],
):
    """_summary_."""
    _man_columns = [
        index_col,
    ] + specific_columns

    _check = [item in columns for item in _man_columns]
    if not all(_check):
        _missing = [item for item, b in zip(_man_columns, _check) if not b]
        msg = f"Missing mandatory exposure columns: {_missing}"
        raise FIATDataError(msg)


def check_exp_derived_types(
    type: str,
    found: tuple | list,
    missing: tuple | list,
):
    """_summary_."""
    # Error when no columns are found for vulnerability type
    if not found:
        msg = f"For type: '{type}' no matching columns were found for \
fn_{type}_* and max_{type}_* columns."
        raise FIATDataError(msg)

    # Log when combination of fn and max is missing
    if missing:
        logger.warning(
            f"No every damage function has a corresponding \
    maximum potential damage: {missing}"
        )


def check_exp_grid_dmfs(
    exp: object,
    dmfs: tuple | list,
):
    """_summary_."""
    _ef = [_i.get_metadata_item("fn_damage") for _i in exp]
    _i = None

    _check = [item in dmfs for item in _ef]
    if not all(_check):
        _missing = [item for item, b in zip(_ef, _check) if not b]
        msg = f"Incorrect damage function identifier found in exposure grid: {_missing}"
        raise FIATDataError(msg)


def check_exp_index_col(
    obj: object,
    index_col: type,
):
    """_summary_."""
    if index_col not in obj.columns:
        raise FIATDataError(f"Index column ('{index_col}') not found in {obj.path}")


## Vulnerability
