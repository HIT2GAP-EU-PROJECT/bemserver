"""Data model for window"""

from .thing import Thing


class Window(Thing):
    """Window description"""

    def __init__(self, name, facade_id, surface_info=None, covering=None,
                 orientation=None, description=None, glazing=None,
                 u_value=None, id=None):
        super().__init__(id=id)
        self.name = name
        self.covering = covering
        self.surface_info = surface_info
        self.facade_id = facade_id
        self.description = description
        self.orientation = orientation
        self.glazing = glazing
        self.u_value = u_value
