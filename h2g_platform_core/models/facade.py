"""Data model for facade"""

from .thing import Thing


class Facade(Thing):
    """Facade model class"""

    def __init__(self, name, spaces, surface_info, building_id,
                 windows_wall_ratio=None, description=None, interior=False,
                 orientation=None, windows=None, id=None):
        super().__init__(id=id)
        self.name = name
        self.spaces = spaces
        self.surface_info = surface_info
        self.windows_wall_ratio = windows_wall_ratio
        self.building_id = building_id
        self.description = description
        self.interior = interior
        self.orientation = orientation
        self.windows = windows or []
