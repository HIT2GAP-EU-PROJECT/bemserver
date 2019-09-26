"""Tests for system data model"""

# from bemserver.models.system import SystemType

from tests import TestCoreModel


class TestModelSystem(TestCoreModel):
    """System model tests"""

    def test_model_system_type_enum(self):
        """Tests on SystemType"""

        # hvac properties
        # assert SystemType.hvac.properties is None
        # assert SystemType.hvac_air_handling_unit.properties is not None
        # assert SystemType.hvac_air_handling_unit.properties.heating
        # assert SystemType.hvac_air_handling_unit.properties.cooling
        # assert SystemType.hvac_air_handling_unit.properties.indoor_air_quality
        # assert SystemType.hvac_boiler.properties is not None
        # assert SystemType.hvac_boiler.properties.heating
        # assert not SystemType.hvac_boiler.properties.cooling
        # assert not SystemType.hvac_boiler.properties.indoor_air_quality
        #
        # # electrical properties
        # assert SystemType.electrical.properties is None
        # assert SystemType.electrical_electric_generator.properties is not None
        # assert not SystemType.electrical_electric_generator.properties.store
        # assert SystemType.electrical_electric_generator.properties.consumer
        # assert SystemType.electrical_electric_generator.properties.producer
        #
        # # parent properties
        # assert SystemType.electrical_solar.properties is not None
        # assert (SystemType.electrical_solar_thermal.properties ==
        #         SystemType.electrical_solar.properties)
        #
        # # hierarchy
        # assert not SystemType.hvac.has_parent
        # assert SystemType.hvac_coil.has_parent
        # assert SystemType.hvac_coil.parent == SystemType.hvac
