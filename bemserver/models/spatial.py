"""Data model for spatial data"""

from .quantity import Quantity

from .thing import Thing


class AbsDimensionInfo(Thing):
    """Abstract class to enapsulate dimensions"""

    KINDS_MAP = {}

    @classmethod
    def get_kinds(cls):
        """returns a mapping attribute name - quantity kind"""
        return cls.KINDS_MAP

    @classmethod
    def get_attr_name(cls, kind):
        '''returns the attribute name based on the kind passed as parameter.
        Used to deserialize elements from the ontology'''
        for attr_name, quantity in cls.KINDS_MAP.items():
            if quantity == kind:
                return attr_name
        return

    def get_quantities(self):
        """Returns a list of quantities associated to the dimensions"""
        res = []
        for attr in self.__class__.get_kinds():
            if getattr(self, attr):
                res.append(Quantity(self.__class__.get_kinds()[attr],
                                    getattr(self, attr)))
        return res


class SpatialInfo(AbsDimensionInfo):
    """Spatial info model class"""

    KINDS_MAP = {'area': 'Area', 'max_height': 'Height', 'volume': 'Volume'}

    def __init__(self, area=None, max_height=None, volume=None):
        super().__init__()
        self.area = area
        self.max_height = max_height
        self.volume = volume


class SurfaceInfo(AbsDimensionInfo):
    """Dimensions for a surface - wall, window..."""

    KINDS_MAP = {'area': 'Area', 'max_height': 'Height', 'width': 'Width'}

    def __init__(self, area=None, max_height=None, width=None):
        super().__init__()
        self.area = area
        self.max_height = max_height
        self.width = width


class OrientedSpatialInfo(Thing):
    """Oriented spatial info model class"""

    def __init__(self, area, orientation):
        super().__init__()
        self.area = area
        self.orientation = orientation
