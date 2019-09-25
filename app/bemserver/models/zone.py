"""Data model for zone"""

# from enum import Enum, unique as enum_unique

from .thing import Thing


# @enum_unique
# class ZoneType(Enum):
#     """Zone kinds"""
#     room = ('Room')
#     floor = ('Floor')
#     desk = ('Desk')
#     other = ('Other')
#
#     def __init__(self, label):
#         self.label = label


class Zone(Thing):
    """Zone model class"""

    def __init__(self, name, zones, spaces, building_id=None,
                 description=None, *, id=None):
        super().__init__(id=id)
        self.name = name
        self.zones = zones or []
        self.spaces = spaces or []
        self.building_id = building_id
        self.description = description
