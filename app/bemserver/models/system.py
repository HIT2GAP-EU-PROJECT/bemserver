"""Data model for systems"""

from abc import ABC, abstractmethod

# from ..tools.custom_enum import HierarchyEnum
from .thing import Thing


# class HVACSystemSpec():
#     """HVAC system attributes"""

#     def __init__(self, heating=False, cooling=False,
#                  indoor_air_quality=False):
#         self.heating = heating
#         self.cooling = cooling
#         self.indoor_air_quality = indoor_air_quality
#
#
# class ElectricalSystemSpec():
#     """Electrical system attributes"""
#
#     def __init__(self, store=False, consumer=False, producer=False):
#         self.store = store
#         self.consumer = consumer
#         self.producer = producer
#
#
# class SystemType(HierarchyEnum):
#     """System types classification (based on the IFC and Haystack)"""
#
#     # HVAC
#     hvac = ('HVAC')
#     hvac_air_handling_unit = (
#         'Air handling unit', 'hvac', HVACSystemSpec(True, True, True))
#     hvac_boiler = ('Boiler', 'hvac', HVACSystemSpec(heating=True))
#     hvac_chiller = ('Chiller', 'hvac', HVACSystemSpec(cooling=True))
#     hvac_burner = ('Burner', 'hvac', HVACSystemSpec(heating=True))
#     hvac_coil = (
#         'Coil', 'hvac', HVACSystemSpec(heating=True, cooling=True))
#     hvac_evaporative_cooler = (
#         'Evaporative cooler', 'hvac', HVACSystemSpec(cooling=True))
#     hvac_engine = ('Engine', 'hvac', HVACSystemSpec(heating=True))
#     hvac_water_plant = ('Water plant', 'hvac', HVACSystemSpec())
#     hvac_steam_plant = ('Steam plant', 'hvac', HVACSystemSpec())
#     hvac_heat_exchanger = (
#         'Heat exchanger', 'hvac', HVACSystemSpec(heating=True, cooling=True))
#     hvac_space_heater = (
#         'Space heater', 'hvac', HVACSystemSpec(heating=True))
#     hvac_air_to_air_heat_recovery = (
#         'Air to air heat recovery', 'hvac', HVACSystemSpec())
#     hvac_humidifier = (
#         'Humidifier', 'hvac', HVACSystemSpec(indoor_air_quality=True))
#     hvac_evaporator = (
#         'Evaporator', 'hvac', HVACSystemSpec(indoor_air_quality=True))
#     hvac_vibration_isolator = (
#         'Vibration isolator', 'hvac', HVACSystemSpec())
#     hvac_chilled_beams = (
#         'Chilled beams', 'hvac', HVACSystemSpec(cooling=True))
#     hvac_fan_coil_unit = (
#         'Fan coil unit', 'hvac', HVACSystemSpec(heating=True, cooling=True))
#     hvac_heat_pump = (
#         'Heat pump', 'hvac', HVACSystemSpec(heating=True, cooling=True))
#     hvac_cooling_tower = (
#         'Cooling tower', 'hvac', HVACSystemSpec(cooling=True))
#     hvac_plant = ('Plant', 'hvac', HVACSystemSpec())
#     hvac_fire_suppression_terminal = (
#         'Fire suppression terminal', 'hvac', HVACSystemSpec())
#     hvac_condenser = ('Condenser', 'hvac', HVACSystemSpec())
#     hvac_compressor = ('Compressor', 'hvac', HVACSystemSpec())
#     hvac_pump = ('Pump', 'hvac', HVACSystemSpec())
#     hvac_tank = ('Tank', 'hvac', HVACSystemSpec())
#     hvac_valve = ('Valve', 'hvac', HVACSystemSpec())
#     hvac_damper = ('Damper', 'hvac', HVACSystemSpec())
#     hvac_fan = ('Fan', 'hvac', HVACSystemSpec())
#
#     # plumbling fire protection
#     plumbling_fire_protection = ('Plumbing fire protection')
#     plumbling_fire_protection_sanitary_terminal = (
#         'Sanitary terminal', 'plumbling_fire_protection')
#     plumbling_fire_protection_stack_terminal = (
#         'Stack terminal', 'plumbling_fire_protection')
#     plumbling_fire_protection_waste_terminal = (
#         'Waste terminal', 'plumbling_fire_protection')
#     plumbling_fire_protection_interceptor = (
#         'Interceptor', 'plumbling_fire_protection')
#     plumbling_fire_protection_fire_suppression_terminal = (
#         'Fire suppression terminal', 'plumbling_fire_protection')
#
#     # electrical
#     electrical = ('Electrical')
#     electrical_electric_flow_storage = (
#         'Electric flow storage', 'electrical',
#         ElectricalSystemSpec(store=True))
#     # audivisual appliance
#     electrical_audiovisual_appliance = (
#         'Audiovisual appliance', 'electrical',
#         ElectricalSystemSpec(consumer=True))
#     electrical_audiovisual_appliance_amplifier = (
#         'Amplifier', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_camera = (
#         'Camera', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_display = (
#         'Display/screen', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_microphone = (
#         'Microphone', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_player = (
#         'Player', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_projector = (
#         'Projector', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_receiver = (
#         'Receiver', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_speaker = (
#         'Speaker', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_switcher = (
#         'Switcher', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_telephone = (
#         'Telephone', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_smartphone_station = (
#         'Smartphone station', 'electrical_audiovisual_appliance')
#     electrical_audiovisual_appliance_tuner = (
#         'Tuner', 'electrical_audiovisual_appliance')
#     # communication appliance
#     electrical_communication_appliance = (
#         'Communication appliance', 'electrical',
#         ElectricalSystemSpec(consumer=True))
#     electrical_communication_appliance_antenna = (
#         'Antenna', 'electrical_communication_appliance')
#     electrical_communication_appliance_computer = (
#         'Computer', 'electrical_communication_appliance')
#     electrical_communication_appliance_fax = (
#         'Fax', 'electrical_communication_appliance')
#     electrical_communication_appliance_gateway = (
#         'Gateway', 'electrical_communication_appliance')
#     electrical_communication_appliance_modem = (
#         'Modem', 'electrical_communication_appliance')
#     electrical_communication_appliance_network = (
#         'Network appliance (bridge, hub, router, repeater)',
#         'electrical_communication_appliance')
#     electrical_communication_appliance_printer = (
#         'Printer', 'electrical_communication_appliance')
#     electrical_communication_appliance_scanner = (
#         'Scanner', 'electrical_communication_appliance')
#     # electric appliance
#     electrical_electric_appliance = (
#         'Electric appliance', 'electrical',
#         ElectricalSystemSpec(consumer=True))
#     electrical_electric_appliance_dishwater = (
#         'Dishwater', 'electrical_electric_appliance')
#     electrical_electric_appliance_boiler = (
#         'Boiler', 'electrical_electric_appliance')
#     electrical_electric_appliance_cooker = (
#         'Cooker', 'electrical_electric_appliance')
#     electrical_electric_appliance_coffee_machine = (
#         'Coffee machine', 'electrical_electric_appliance')
#     electrical_electric_appliance_fs_electric_heater = (
#         'FS electric heater', 'electrical_electric_appliance')
#     electrical_electric_appliance_fs_fan = (
#         'FS fan', 'electrical_electric_appliance')
#     electrical_electric_appliance_fs_water_heater = (
#         'FS water heater', 'electrical_electric_appliance')
#     electrical_electric_appliance_fs_water_cooler = (
#         'FS water cooler', 'electrical_electric_appliance')
#     electrical_electric_appliance_freezer = (
#         'Freezer', 'electrical_electric_appliance')
#     electrical_electric_appliance_fridge = (
#         'Fridge', 'electrical_electric_appliance')
#     electrical_electric_appliance_hand_dryer = (
#         'Hand dryer', 'electrical_electric_appliance')
#     electrical_electric_appliance_kitchen_device = (
#         'Kitchen device', 'electrical_electric_appliance')
#     electrical_electric_appliance_microwave = (
#         'Microwave', 'electrical_electric_appliance')
#     electrical_electric_appliance_photocopier = (
#         'Photocopier', 'electrical_electric_appliance')
#     electrical_electric_appliance_refrigerator = (
#         'Refrigerator', 'electrical_electric_appliance')
#     electrical_electric_appliance_tumble_dryer = (
#         'Tumble dryer', 'electrical_electric_appliance')
#     electrical_electric_appliance_vending_machine = (
#         'Vending machine', 'electrical_electric_appliance')
#     electrical_electric_appliance_washing_machine = (
#         'Washing machine', 'electrical_electric_appliance')
#     # transformer
#     electrical_transformer = (
#         'Transformer', 'electrical', ElectricalSystemSpec())
#     # electric generator
#     electrical_electric_generator = (
#         'Electric generator', 'electrical',
#         ElectricalSystemSpec(consumer=True, producer=True))
#     # electric generator
#     electrical_electric_motor = (
#         'Electric motor', 'electrical',
#         ElectricalSystemSpec(consumer=True, producer=True))
#     # electric generator
#     electrical_electric_time_control = (
#         'Electric time control', 'electrical', ElectricalSystemSpec())
#     # lamp
#     electrical_lamp = (
#         'Lamp', 'electrical', ElectricalSystemSpec(consumer=True))
#     electrical_lamp_desk_light = ('Desk light', 'electrical_lamp')
#     electrical_lamp_central_light = ('Central light', 'electrical_lamp')
#     # lamp
#     electrical_solar = (
#         'Solar', 'electrical', ElectricalSystemSpec(producer=True))
#     electrical_solar_electric = ('Solar electric', 'electrical_solar')
#     electrical_solar_thermal = ('Solar thermal', 'electrical_solar')
#
#     # monitoring
#     monitoring = ('Monitoring')
#     monitoring_sensor = ('Sensor', 'monitoring')
#     monitoring_actuator = ('Actuator', 'monitoring')
#     monitoring_alarm = ('Alarm', 'monitoring')
#     monitoring_controller = ('Controller', 'monitoring')
#     monitoring_meter = ('Meter', 'monitoring')
#
#     # wearable
#     wearable = ('Wearable')
#     wearable_smartwatch = ('Smartwatch', 'wearable')
#     wearable_smartphone = ('Smartphone', 'wearable')
#
#     def __init__(self, label, parent_name=None, spec=None):
#         HierarchyEnum.__init__(self, label=label, parent_name=parent_name)
#         self._properties = spec
#
#     @property
#     def properties(self):
#         """Return specific properties or None"""
#         cur_item = self
#         while cur_item._properties is None and cur_item.has_parent:
#             cur_item = cur_item.parent
#         return cur_item._properties


class Localization():
    """Localization class - associated to a system"""

    def __init__(self, site_id=None, building_id=None, floor_id=None,
                 space_id=None):
        if not site_id and not building_id and not floor_id and not space_id:
            raise Exception('No localization specified')
        self.site_id = site_id
        self.building_id = building_id
        self.floor_id = floor_id
        self.space_id = space_id


class System(Thing, ABC):
    """Abstract class for systems"""

    @abstractmethod
    def __init__(self, name, localization, description=None, id=None):
        super().__init__(id=id)
        self.name = name
        self.description = description
        self.localization = localization
