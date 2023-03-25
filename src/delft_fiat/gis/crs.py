from osgeo import osr


class CRS:
    def __init__(
        self,
        srs: osr.SpatialReference,
    ):
        pass

    def __del__(self):
        pass

    def __eq__(self):
        pass

    @classmethod
    def from_user_input(
        cls,
        user_input: str,
    ):
        return cls()
