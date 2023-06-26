from delft_fiat.io import BufferTextHandler
from delft_fiat.gis import geom, overlay
from delft_fiat.models.calc import get_inundation_depth
from delft_fiat.util import NEWLINE_CHAR, _pat, replace_empty

from math import isnan
from pathlib import Path


def geom_worker(
    path: Path,
    haz: "GridSource",
    idx: int,
    exp: "TableLazy",
    exp_geom: "GeomSource",
    vul: "Table",
):
    """_summary_"""

    _band_name = ""
    if haz.count != 1:
        _band_name = haz.get_band_name(idx)

    writer = BufferTextHandler(
        Path(path, f"{idx:03d}.dat"),
        buffer_size=100000,
    )
    header = (
        f"{exp.meta['index_name']},".encode()
        + ",".join(exp.create_specific_columns(_band_name)).encode()
        + NEWLINE_CHAR.encode()
    )
    writer.write(header)

    for ft in exp_geom:
        row = b""

        ft_info_raw = exp[ft.GetField(0)]
        ft_info = replace_empty(_pat.split(ft_info_raw))
        ft_info = [x(y) for x, y in zip(exp.dtypes, ft_info)]
        row += f"{ft_info[exp.index_col]}".encode()

        if ft_info[exp._columns["Extraction Method"]].lower() == "area":
            res = overlay.clip(haz[idx], haz.get_srs(), haz.get_geotransform(), ft)
        else:
            res = overlay.pin(haz[idx], haz.get_geotransform(), geom.point_in_geom(ft))
        inun, redf = get_inundation_depth(
            res,
            "DEM",
            ft_info[exp._columns["Ground Floor Height"]],
        )
        row += f",{round(inun, 2)},{round(redf, 2)}".encode()

        _td = 0
        for key, col in exp.damage_function.items():
            if isnan(inun) or ft_info[col] == "nan":
                _d = ""
            else:
                _df = vul[round(inun, 2), ft_info[col]]
                _d = _df * ft_info[exp.max_potential_damage[key]] * redf
                _d = round(_d, 2)
                _td += _d

            row += f",{_d}".encode()

        row += f",{round(_td, 2)}".encode()

        row += NEWLINE_CHAR.encode()
        writer.write(row)

    writer.flush()
    writer = None
