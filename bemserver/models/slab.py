"""Data model for slab. A slab is typically a vertical element that supports
some load."""

from .thing import Thing


class Slab(Thing):
    """Slab model class"""

    def __init__(self, name, floors, surface_info, building_id,
                 description=None, kind=None, windows=None, id=None):
        super().__init__(id=id)
        self.name = name
        self.floors = floors
        self.surface_info = surface_info
        self.building_id = building_id
        self.description = description
        self.windows = windows or []
        self.kind = kind
