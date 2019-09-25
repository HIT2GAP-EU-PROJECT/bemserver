"""Data model for building"""

from .thing import Thing
from .quantity import Quantity


# TODO: add relations with energy used and systems
class Building(Thing):
    """Building model class"""

    def __init__(self, name, kind, site_id, area=None, description=None, *,
                 id=None):
        super().__init__(id=id)
        self.name = name
        self.kind = kind
        self.area = area
        self.site_id = site_id
        self.description = description

    def quantities(self):
        """Get building's dimensions as a list of properties.

        :return List: a list of Quantity objects"""
        if self.area is not None:
            return [Quantity("Area", self.area)]
        return []
