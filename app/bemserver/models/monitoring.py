"""Data model for window"""

from .system import System
from .thing import Thing


class MeasureValueProperties():
    """Properties of measures - properties specific to the values of measures
    """

    def __init__(self, vmax=None, vmin=None, frequency=None):
        self.vmax = vmax
        self.vmin = vmin
        self.frequency = frequency


class MeasureMaterialProperties():
    """Properties specific to the material used"""

    def __init__(self, latency=None, precision=None, accuracy=None,
                 sensitivity=None):
        self.latency = latency
        self.accuracy = accuracy
        self.precision = precision
        self.sensitivity = sensitivity


class Location:
    """Location. Use in Measure to refer to some location in a site"""

    def __init__(self, id, type=None):
        self.id = id
        self.type = type


class Measure(Thing):
    """Measure description"""

    def __init__(self, sensor_id, unit, medium=None, observation_type=None,
                 description=None, id=None, material_properties=None,
                 value_properties=None, on_index=False, outdoor=False,
                 associated_locations=None, method=None, external_id=None,
                 set_point=False, ambient=None):
        super().__init__(id=id)
        self.sensor_id = sensor_id
        self.description = description
        self.material_properties = material_properties
        self.value_properties = value_properties
        self.medium = medium
        self.observation_type = observation_type
        self.unit = unit
        self.associated_locations = associated_locations or []
        self.on_index = on_index
        self.outdoor = outdoor
        self.external_id = external_id
        self.method = method or 'Frequency'
        self.set_point = set_point
        self.ambient = ambient

    def add_external_id(self, ext_id):
        self.external_id = ext_id


class Sensor(System):
    """Sensor description"""

    def __init__(self, name, static=True, system_id=None, localization=None,
                 description=None, measures=None, id=None):
        if not system_id and not localization:
            raise Exception
        super().__init__(name, localization=localization,
                         description=description, id=id)
        self.static = static
        self.system_id = system_id
        self.measures = measures or []
