"""Data model for occupancy"""

from enum import Enum, unique as enum_unique

from .thing import Thing
from ..tools.custom_enum import HierarchyEnum

# from . import SystemType
# from .exceptions import OccupantUnknownElectronicFamilyError


@enum_unique
class AgeCategory(Enum):
    """Occupant's age category"""
    not_available = ('Not available')
    ac_15_24 = ('15-24')
    ac_25_34 = ('25-34')
    ac_35_44 = ('35-44')
    ac_45_54 = ('45-54')
    ac_55_64 = ('55-64')
    ac_65 = ('65+')

    def __init__(self, label):
        self.label = label


@enum_unique
class DistanceToPointType(Enum):
    """Occupants' perceptions of distance to a point"""
    not_available = ('Not available')
    far = ('Far')
    near = ('Near')
    in_between = ('In between')

    def __init__(self, label):
        self.label = label


@enum_unique
class KnowledgeLevel(Enum):
    """Occupants' knowledge level"""
    not_available = ('Not available')
    very_low = ('Very low')
    low = ('Low')
    medium = ('Medium')
    high = ('High')
    very_high = ('Very high')

    def __init__(self, label):
        self.label = label


@enum_unique
class ActivityFrequency(Enum):
    """Occupants' activity frequency"""
    not_available = ('Not available')
    regularly = ('Regularly')
    occasionally = ('Occasionally')
    never = ('Never')

    def __init__(self, label):
        self.label = label


@enum_unique
class WorkspaceType(Enum):
    """Workspace types"""
    not_available = ('Not available',)
    office = ('Office')

    def __init__(self, label):
        self.label = label


class OccupantWorkSchedule(Thing):
    """Occupant work schedule class"""

    def __init__(self, day, time_start, time_end):
        super().__init__()
        self.day = day
        self.time_start = time_start
        self.time_end = time_end


class OccupantWorkspace(Thing):
    """Occupant workspace class"""

    def __init__(self, kind, desk_location_window, desk_location_heater=None,
                 desk_location_airconditioner=None):
        super().__init__()
        self.kind = kind
        self.desk_location_window = desk_location_window
        self.desk_location_heater = desk_location_heater
        self.desk_location_airconditioner = desk_location_airconditioner


class OccupantEnergyBehaviour(Thing):
    """Occupant energy behaviour class"""

    def __init__(self, awareness_activities, awareness_level=None):
        super().__init__()
        self.awareness_activities = awareness_activities
        self.awareness_level = awareness_level


class OccupantComfortOperationFrequency(Thing):
    """Occupant comfort operation frequency class"""

    def __init__(self, window_shades, curtains, thermostat, portable_fan,
                 ceiling_fan, ceiling_air_ventilation, floor_air_ventilation,
                 light_switch, light_dimmer, desk_light, hvac_unit,
                 other_1=None, other_2=None):
        super().__init__()
        self.window_shades = window_shades
        self.curtains = curtains
        self.thermostat = thermostat
        self.portable_fan = portable_fan
        self.ceiling_fan = ceiling_fan
        self.ceiling_air_ventilation = ceiling_air_ventilation
        self.floor_air_ventilation = floor_air_ventilation
        self.light_switch = light_switch
        self.light_dimmer = light_dimmer
        self.desk_light = desk_light
        self.hvac_unit = hvac_unit
        self.other_1 = other_1
        self.other_2 = other_2


class OccupantElectronicUsedQuantity(Thing):
    """Occupant electronic used quantity class"""

    def __init__(self, electronic_kind, number):
        super().__init__()
        self.electronic_kind = electronic_kind
        self.number = number


class OccupantElectronicUsed(Thing):
    """Occupant electronic used class"""

    def __init__(self, number_connected_device_at_desk,
                 electronic_used_in_workspace=None):
        super().__init__()
        self.number_connected_device_at_desk = number_connected_device_at_desk
        self.electronic_used_in_workspace = electronic_used_in_workspace


class Occupant(Thing):
    """Occupant class"""

    def __init__(self, gender, age_category, work_schedule=None,
                 workspace=None, energy_behaviour=None, electronics=None,
                 comfort_operation_frequencies=None, token_id=None):
        super().__init__()
        self.gender = gender
        self.age_category = age_category
        self.work_schedule = work_schedule
        self.workspace = workspace
        self.energy_behaviour = energy_behaviour
        self.electronics = electronics
        self.comfort_operation_frequencies = comfort_operation_frequencies
        self.token_id = token_id

    # @classmethod
    # def get_electronic_families(cls):
    #     """Return available electronics family for occupant profile"""
    #     return [
    #         SystemType.electrical_audiovisual_appliance,
    #         SystemType.electrical_communication_appliance,
    #         SystemType.electrical_lamp,
    #         SystemType.electrical_electric_appliance]
    #
    # @classmethod
    # def get_electronic_types_by_family(cls, family_type_name):
    #     """Return available electronics type by family for occupant profile
    #     """
    #     try:
    #         family_type = SystemType[family_type_name]
    #     except KeyError:
    #         raise OccupantUnknownElectronicFamilyError()
    #
    #     if family_type not in cls.get_electronic_families():
    #         raise OccupantUnknownElectronicFamilyError()
    #
    #     return [
    #         cur_type for cur_type in list(SystemType)
    #         if cur_type.parent == family_type]
    #
    # @classmethod
    # def get_all_electronic_types(cls):
    #     """Return all available electronics type for occupant profile"""
    #     electronic_families = cls.get_electronic_families()
    #
    #     return [
    #         cur_type for cur_type in list(SystemType)
    #         if cur_type.parent in electronic_families]


@enum_unique
class PreferenceType(Enum):
    """Preference types"""

    lower = ('Lower')
    as_now = ('As now')
    higher = ('Higher')

    def __init__(self, label):
        self.label = label


class ComfortType(HierarchyEnum):
    """Comfort aspects types"""

    # Acoustic comfort
    acoustic = ('Acoustic',)

    # Visual comfort
    visual = ('Visual',)
    visual_harmony = ('Harmony', 'visual')
    visual_too_dark = ('Too dark', 'visual')
    visual_too_bright = ('Too bright', 'visual')

    # Air comfort
    air = ('Air',)
    air_quality = ('Quality', 'air')
    air_temperature = ('Temperature', 'air')
    air_humidity = ('Humidity', 'air')
    air_velocity = ('Velocity', 'air')

    # Equipment comfort
    equipment = ('Equipment',)
    equipment_seats = ('Seats', 'equipment')
    equipment_desk = ('Desk', 'equipment')
    equipment_it = ('IT', 'equipment')

    # Uniformity comfort
    uniformity = ('Uniformity',)
    uniformity_spatial = ('Spatial', 'uniformity')
    uniformity_temporal = ('Temporal', 'uniformity')


class ComfortPerception(Thing):
    """Comfort Perception class"""

    def __init__(self, aspect_type, perception, satisfaction, preference):
        super().__init__()
        self.aspect_type = aspect_type
        self.perception = perception
        self.satisfaction = satisfaction
        self.preference = preference


class Comfort(Thing):
    """Comfort class"""

    def __init__(self, occupant_id, time, perceptions, description=None):
        super().__init__()
        self.occupant_id = occupant_id
        self.time = time
        self.perceptions = perceptions
        self.description = description
