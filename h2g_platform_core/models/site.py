"""Data model for site"""

from .thing import Thing


class Site(Thing):
    """Site model class"""

    def __init__(self, name, geographic_info, description=None, *, id=None):
        super().__init__(id=id)
        self.name = name
        self.geographic_info = geographic_info
        self.description = description
