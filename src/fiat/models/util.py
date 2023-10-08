from fiat.gis import geom, overlay
from fiat.io import BufferTextHandler, GridSource
from fiat.log import LogItem, Sender
from fiat.models.calc import calc_haz
from fiat.util import NEWLINE_CHAR, _pat, replace_empty

from math import isnan
from numpy import full, ravel, unravel_index, where
from osgeo import gdal, osr
from pathlib import Path


def geom_worker(
    cfg: "ConfigReader",
    queue: "queue.Queue",
    haz: GridSource,
    idx: int,
    vul: "Table",
    exp: "TableLazy",
    exp_geom: dict,
):
    """_summary_"""

    # Extract the hazard band as an object
    band = haz[idx]
    # Setup some metadata
    _band_name = cfg["hazard.band_names"][idx - 1]
    _ref = cfg.get("hazard.elevation_reference")
    _rnd = cfg.get("vulnerability.round")
    vul_min = min(vul.index)
    vul_max = max(vul.index)

    # Setup the write and write the header
    writer = BufferTextHandler(
        Path(cfg.get("output.path.tmp"), f"{idx:03d}.dat"),
        buffer_size=100000,
    )
    header = (
        f"{exp.meta['index_name']},".encode()
        + ",".join(exp.create_specific_columns(_band_name)).encode()
        + NEWLINE_CHAR.encode()
    )
    writer.write(header)

    # Setup connection with the main process for missing values:
    _sender = Sender(queue=queue)

    # Loop over all the datasets
    for _, gm in exp_geom.items():
        # Loop over all the geometries
        for ft in gm:
            row = b""

            # Acquire data from exposure database
            ft_info_raw = exp[ft.GetField(0)]
            if ft_info_raw is None:
                _sender.emit(
                    LogItem(
                        2,
                        f"Object with ID: {ft.GetField(0)} -> No data found in exposure database",
                    )
                )
                continue
            ft_info = replace_empty(_pat.split(ft_info_raw))
            ft_info = [x(y) for x, y in zip(exp.dtypes, ft_info)]
            row += f"{ft_info[exp.index_col]}".encode()

            # Get the hazard data from the exposure geometrie
            if ft_info[exp._columns["Extraction Method"]].lower() == "area":
                res = overlay.clip(band, haz.get_srs(), haz.get_geotransform(), ft)
            else:
                res = overlay.pin(band, haz.get_geotransform(), geom.point_in_geom(ft))

            # Calculate the inundation
            inun, redf = calc_haz(
                res,
                _ref,
                ft_info[exp._columns["Ground Floor Height"]],
                ft_info[exp._columns["Ground Elevation"]],
            )
            row += f",{round(inun, 2)},{round(redf, 2)}".encode()

            # Calculate the damage per catagory, and in total (_td)
            _td = 0
            for key, col in exp.damage_function.items():
                if isnan(inun) or str(ft_info[col]) == "nan":
                    _d = "nan"
                else:
                    inun = max(min(vul_max, inun), vul_min)
                    _df = vul[round(inun, _rnd), ft_info[col]]
                    _d = _df * ft_info[exp.max_potential_damage[key]] * redf
                    _d = round(_d, 2)
                    _td += _d

                row += f",{_d}".encode()

            row += f",{round(_td, 2)}".encode()

            # Write this to the buffer
            row += NEWLINE_CHAR.encode()
            writer.write(row)

    # Flush the buffer to the drive and close the writer
    writer.flush()
    writer = None


def grid_worker_exact(
    cfg: "ConfigReader",
    haz: GridSource,
    idx: int,
    vul: "Table",
    exp: GridSource,
):
    """_summary_"""

    # Set some variables for the calculations
    exp_bands = []
    write_bands = []
    exp_nds = []
    dmfs = []

    # Extract the hazard band as an object
    haz_band = haz[idx]
    # Set the output directory
    _out = cfg.get("output.path")
    if cfg.get("hazard.risk"):
        _out = cfg.get("hazard.path.risk")

    # Create the outgoing netcdf containing every exposure damages
    out_src = GridSource(
        Path(_out, "output.nc"),
        mode="w",
    )
    out_src.create(
        exp.shape,
        exp.count,
        exp.dtype,
        options=["FORMAT=NC4", "COMPRESS=DEFLATE"],
    )
    out_src.set_srs(exp.get_srs())
    out_src.set_geotransform(exp.get_geotransform())
    # Create the outgoing total damage grid
    td_out = GridSource(
        Path(
            _out,
            "total_damages.nc",
        ),
        mode="w",
    )
    td_out.create(
        exp.shape,
        1,
        exp.dtype,
        options=["FORMAT=NC4", "COMPRESS=DEFLATE"],
    )
    td_out.set_geotransform(exp.get_geotransform())
    td_out.set_srs(exp.get_srs())
    td_band = td_out[1]
    td_noval = -0.5 * 2**128
    td_band.src.SetNoDataValue(td_noval)

    for idx in range(exp.count):
        exp_bands.append(exp[idx + 1])
        write_bands.append(out_src[idx + 1])
        exp_nds.append(exp_bands[idx].nodata)
        write_bands[idx].src.SetNoDataValue(exp_nds[idx])
        dmfs.append(exp_bands[idx].get_metadata_item("damage_function"))

    for _w, h_ch in haz_band:
        td_ch = td_band[_w]

        for idx, exp_band in enumerate(exp_bands):
            e_ch = exp_band[_w]

            out_ch = full(e_ch.shape, exp_nds[idx])
            e_ch = ravel(e_ch)
            _coords = where(e_ch != exp_nds[idx])[0]
            if len(_coords) == 0:
                write_bands[idx].src.WriteArray(out_ch, *_w[:2])
                continue

            e_ch = e_ch[_coords]
            h_1d = ravel(h_ch)
            h_1d = h_1d[_coords]
            _hcoords = where(h_1d != haz_band.nodata)[0]

            if len(_hcoords) == 0:
                write_bands[idx].src.WriteArray(out_ch, *_w[:2])
                continue

            _coords = _coords[_hcoords]
            e_ch = e_ch[_hcoords]
            h_1d = h_1d[_hcoords]
            h_1d.clip(min(vul.index), max(vul.index))

            dmm = [vul[round(float(n), 2), dmfs[idx]] for n in h_1d]
            e_ch = e_ch * dmm

            idx2d = unravel_index(_coords, *[exp._chunk])
            out_ch[idx2d] = e_ch

            write_bands[idx].write_chunk(out_ch, _w[:2])

            td_1d = td_ch[idx2d]
            td_1d[where(td_1d == td_noval)] = 0
            td_1d += e_ch
            td_ch[idx2d] = td_1d

        td_band.write_chunk(td_ch, _w[:2])

    for _w in write_bands[:]:
        w = _w
        write_bands.remove(_w)
        w.flush()
        w = None

    exp_bands = None
    td_band.flush()
    td_band = None
    td_out = None

    out_src.flush()
    out_src = None

    haz_band = None


def grid_worker_loose():
    """_summary_"""

    pass
