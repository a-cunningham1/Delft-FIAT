import io
from ast import literal_eval


def _Parse_CSV(obj, raw):
    meta = {}
    hdrs = []
    data = ""
    for line in raw.readlines():
        if line.startswith("#"):
            pass
            continue
        if line[0].isalpha():
            hdrs = [item.strip("\n") for item in line.split(",")]
            continue
        if not line:
            break
        data += line
    data = dict(
        zip(
            hdrs,
            tuple(
                zip(
                    *[
                        [*map(literal_eval, item.split(","))]
                        for item in data.split("\n")
                        if item
                    ]
                )
            ),
        )
    )
    obj.meta = meta
    obj.hdrs = hdrs
    obj.data = data


class CSVStruct:
    def __init__(
        self,
        raw: io.TextIOWrapper,
    ):
        # Create body of struct
        _Parse_CSV(self, raw)

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
        repr += f"{'...':6s}, ...\n"
        repr += ")"
        return repr

    def mean():
        pass

    def max():
        pass


def ReadCSV(path):
    f = open(path, "r")
    return CSVStruct(f)


def WriteCSV():
    pass


if __name__ == "__main__":
    f = open(
        r"C:\CODING\PYTHON_DEV\Delft_FIAT\tmp\Database\Vulnerability\h_struct_543.csv"
    )
    c = CSVStruct(f)
    pass
