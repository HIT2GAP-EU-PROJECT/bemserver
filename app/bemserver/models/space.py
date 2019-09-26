"""Data model for space"""

from .thing import Thing


class SpaceOccupancy(Thing):
    """Occupancy description of a space"""

    def __init__(self, nb_permanents=None, nb_max=None):
        super().__init__()
        self.nb_permanents = nb_permanents
        self.nb_max = nb_max


class Space(Thing):
    """Space model class"""

    def __init__(self, name, floor_id, kind=None, occupancy=None,
                 spatial_info=None, description=None, *, id=None):
        super().__init__(id=id)
        self.name = name
        self.kind = kind
        self.occupancy = occupancy
        self.spatial_info = spatial_info
        self.floor_id = floor_id
        self.description = description
