from delft_fiat.gis import geom, overlay
from delft_fiat.io import BufferTextHandler, GridSource
from delft_fiat.log import LogItem, Sender
from delft_fiat.models.calc import calc_haz
from delft_fiat.util import NEWLINE_CHAR, _pat, replace_empty

from math import isnan
from numpy import full, ravel, unravel_index, where
from osgeo import gdal, osr
from pathlib import Path


def geom_worker(
    cfg: "ConfigReader",
    queue: "queue.Queue",
    haz: "GridSource",
    idx: int,
    vul: "Table",
    exp: "TableLazy",
    exp_geom: dict,
):
    """_summary_"""

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
                res = overlay.clip(haz[idx], haz.get_srs(), haz.get_geotransform(), ft)
            else:
                res = overlay.pin(
                    haz[idx], haz.get_geotransform(), geom.point_in_geom(ft)
                )

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
    haz: "GridSource",
    idx: int,
    vul: "Table",
    exp: "GridSource",
):
    """_summary_"""

    exp_nd = exp[1].nodata
    dmf = exp[1].get_metadata_item("damage_function")

    out_src = GridSource(
        "C:\\temp\\output.nc",
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

    for _bandn in range(exp.count):
        write_band = out_src[_bandn + 1]
        write_band.src.SetNoDataValue(exp_nd)

        for (_, h_ch), (_w, e_ch) in zip(haz[idx], exp[_bandn + 1]):
            out_ch = full(e_ch.shape, exp_nd)
            e_ch = ravel(e_ch)
            _coords = where(e_ch != exp_nd)[0]
            if len(_coords) == 0:
                write_band.src.WriteArray(out_ch, *_w[:2])
                continue

            e_ch = e_ch[_coords]
            h_ch = ravel(h_ch)
            h_ch = h_ch[_coords]
            _hcoords = where(h_ch != haz[idx].nodata)[0]

            if len(_hcoords) == 0:
                write_band.src.WriteArray(out_ch, *_w[:2])
                continue

            _coords = _coords[_hcoords]
            e_ch = e_ch[_hcoords]
            h_ch = h_ch[_hcoords]
            h_ch.clip(min(vul.index), max(vul.index))

            dmm = [vul[round(float(n), 2), dmf] for n in h_ch]
            e_ch = e_ch * dmm

            idx2d = unravel_index(_coords, *[exp._chunk])
            out_ch[idx2d] = e_ch

            write_band.write_chunk(out_ch, _w[:2])

        write_band.flush()
        write_band = None
    out_src.flush()
    out_src = None

    pass


def grid_worker_loose():
    """_summary_"""

    pass
