from delft_fiat.util import _detertype

import regex


def _Parse_CSV(
    obj,
):
    """_summary_"""

    meta = {}
    _meta = {}
    hdrs = []

    obj.Handler.seek(0)

    while True:
        line = obj.Handler.readline().decode()
        if line.startswith("#"):
            key, item = line.strip().split("=")
            meta[key.strip().replace("#", "")] = item.strip()
        else:
            hdrs = [item.strip() for item in line.split(",")]
            break

    obj.Handler.skip = obj.Handler.tell()
    t = obj.Handler.readline().strip()
    obj.re = regex.compile(rb'"[^"]*"(*SKIP)(*FAIL)|,')
    obj.dtypes = [_detertype(elem.decode()) for elem in obj.re.split(t)]
    obj.Handler.seek(obj.Handler.skip)

    obj._meta = _meta
    obj.meta = meta
    obj.hdrs = hdrs
