from fiat.cfg import ConfigReader
from fiat.log import Log
from fiat.models import GeomModel, GridModel

from pathlib import Path


class FIAT:
    def __init__(self, cfg: ConfigReader):
        """_summary_

        Parameters
        ----------
        cfg : ConfigReader
            _description_
        """

        self.cfg = cfg

    @classmethod
    def from_path(
        cls,
        file: str,
    ):
        """_summary_"""

        file = Path(file)
        if not Path(file).is_absolute():
            file = Path(Path.cwd(), file)
        cfg = ConfigReader(file)

        return cls(cfg)

    def run(self):
        """_summary_"""

        model = GeomModel(self.cfg)
        model.run()


if __name__ == "__main__":
    pass
