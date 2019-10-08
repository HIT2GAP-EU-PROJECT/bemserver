"""Model for the quantity-related elements.

This module includes all relevant elements for observations on devices,
physical properties in the systems of buildings, and also dimensions
on a building
"""


class Quantity():
    """Class for quantities. Tuple <kind, value, unit>"""

    DEFAULT_UNIT = {'Area': 'SquareMeter',
                    'Height': 'Meter',
                    'Width': 'Meter',
                    'Volume': 'CubeMeter'}

    def __init__(self, kind, value, unit=None):
        self.kind = kind
        self.value = value
        self.unit = unit or self.DEFAULT_UNIT[kind]
