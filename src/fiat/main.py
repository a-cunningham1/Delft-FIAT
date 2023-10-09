from fiat.cfg import ConfigReader
from fiat.log import spawn_logger
from fiat.models import GeomModel, GridModel

from pathlib import Path

logger = spawn_logger("fiat.main")


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
            logger.info("Setting up geom model..")
            model = GeomModel(self.cfg)
            model.run()
        if _models[1]:
            logger.info("Setting up grid model..")
            model = GridModel(self.cfg)
            model.run()


if __name__ == "__main__":
    pass
