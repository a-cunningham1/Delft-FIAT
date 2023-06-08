from delft_fiat.cfg import ConfigReader
from delft_fiat.log import Log
from delft_fiat.models import GeomModel, GridModel

from pathlib import Path


class FIAT:
    def __init__(self, file: str):
        """_summary_

        Parameters
        ----------
        file : str
            _description_
        """
        file = Path(file)
        if not Path(file).is_absolute():
            file = Path(Path.cwd(), file)
        self.cfg = ConfigReader(file)

    def run(self):
        model = GeomModel(self.cfg)
        model.run()


if __name__ == "__main__":
    pass
