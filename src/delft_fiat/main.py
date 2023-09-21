from delft_fiat.cfg import ConfigReader
from delft_fiat.log import Log
from delft_fiat.models import GeomModel, GridModel

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

        _models = self.cfg.get_model_type()
        if _models[0]:
            model = GeomModel(self.cfg)
            model.run()
        if _models[1]:
            model = GridModel(self.cfg)
            model.run()


if __name__ == "__main__":
    pass
