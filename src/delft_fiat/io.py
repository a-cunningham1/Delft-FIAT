from delft_fiat.error import DriverNotFoundError
from delft_fiat.parsing import _Parse_CSV
from delft_fiat.util import Path, _GeomDriverTable, _GridDriverTable, _detertype

import os
import regex
from abc import ABCMeta
from io import BufferedReader, FileIO
from math import nan
from osgeo import gdal, ogr
from osgeo import osr


## Handlers
class FileHandler(BufferedReader):
    def __init__(
        self,
        file: str,
    ) -> "FileHandler":
        """_summary_

        Parameters
        ----------
        file : str
            _description_

        Returns
        -------
        FileHandler
            _description_
        """
        self.Path = file
        super().__init__(FileIO(file))
        self.Skip = 0
        self.Size = sum(1 for _ in self)
        self.seek(self.Skip)

    def __del__(self):
        self.flush()
        self.close()

    def __repr__(self):
        return f"<io.{self.__class__.__name__} file='{self.Path}' encoding=''>"

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        self.seek(self.Skip)
        return False

    def ReadLineOnce(self):
        line = self.readline()
        self._skip += len(line)
        self.flush()
        return line


## Parsing
def _Parse_CSV(
    obj,
):
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


## Structs
class CSV(metaclass=ABCMeta):
    def __init__(
        self,
        file: str,
    ):
        self.Handler = FileHandler(file)
        # Create body of struct
        _Parse_CSV(
            self,
        )

    def __iter__(self):
        pass

    def __repr__(self) -> str:
        return super().__repr__()


class CSVLarge(CSV):
    def __init__(
        self,
        file: str,
    ):
        CSV.__init__(self, file)

        self.index = [None] * self.Handler.Size
        self.lines = [None] * self.Handler.Size
        self.lines[0] = self.Handler.Skip
        with self.Handler as h:
            c = 0
            while True:
                line = h.readline().strip()
                if not line:
                    break
                z = self.re.split(line)[1]
                self.index[c + 1] = z.decode()
                self.lines[c + 1] = len(line) + 2
                c += 1

    def Select(
        self,
        oid: str,
    ):
        if not oid in self.index:
            return None

        idx = self.index.index(oid)
        l = sum(self.lines[0:idx])
        self.Handler.seek(l)
        return [
            elem.decode() for elem in self.re.split(self.Handler.readline().strip())
        ]


class CSVSmall(CSV):
    def __init__(
        self,
        file: str,
    ):
        CSV.__init__(self, file)

        def replace_empty(l):
            return ["nan" if not e else e.decode() for e in l]

        with self.Handler as h:
            b = [replace_empty(self.re.split(line.strip())) for line in h.readlines()]

        self.Handler = None

        self.data = dict(
            zip(self.hdrs, [tuple(map(x, y)) for x, y in zip(self.dtypes, zip(*b))])
        )

    def __iter__(self):
        pass

    def __getitem__(self):
        pass

    def __eq__(self):
        pass

    def __repr__(self):
        repr = "CSVStruct(\n"
        repr += ", ".join([f"{item:6s}" for item in self.hdrs]) + "\n"
        m = zip(*[row[0:3] for row in [*self.data.values()]])
        for item in m:
            repr += ", ".join([f"{str(val):6s}" for val in item]) + "\n"
        repr += f"{'...':6s}, ... )\n"
        return repr

    def mean():
        pass

    def max():
        pass


## Reading
def ReadCSV(
    file: str,
) -> CSV:
    """_summary_

    Parameters
    ----------
    file : str
        _description_

    Returns
    -------
    CSV
        _description_
    """

    size = 20 * 1024 * 1024
    if os.path.getsize(file) < size:
        return CSVSmall(file)
    else:
        return CSVLarge(file)


def ReadGeomFile(
    file: str,
    code: str,
):
    if not Path(file).suffix in _GeomDriverTable:
        raise DriverNotFoundError("")
    driver = ogr.GetDriverByName(_GeomDriverTable[Path(file).suffix])
    src = driver.Open(file)
    return src


def ReadGridFile(
    file: str,
    code: str,
):
    if not Path(file).suffix in _GridDriverTable:
        raise DriverNotFoundError("")
    src = gdal.Open(file)
    return src


##Writing
class WriteGeomFile:
    def __init__(self):
        pass


if __name__ == "__main__":
    f = FileHandler(
        r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\Database\Vulnerability\h_struct_370.csv"
    )
    with f as _f:
        print(_f.readline())
    print(f.read())
    d = CSVSmall(
        r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\Database\Vulnerability\h_struct_370.csv"
    )
    pass
