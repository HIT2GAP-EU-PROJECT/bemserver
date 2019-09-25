"""Data model for floor"""

from .thing import Thing


class Floor(Thing):
    """Floor model class"""

    def __init__(self, name, level, building_id, kind, description=None,
                 spatial_info=None, *, id=None):
        super().__init__(id=id)
        self.name = name
        self.kind = kind
        self.level = level
        self.spatial_info = spatial_info
        self.description = description
        self.building_id = building_id
