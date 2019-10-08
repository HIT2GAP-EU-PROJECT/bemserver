"""Tests for a a ontology inteface so as to build enumerations"""

import pytest

from bemserver.database.db_enums import DBEnumHandler

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestDBEnum(TestCoreDatabaseOntology):
    """Tests on the interface to handle enumerated types in the ontology."""

    def test_db_enums_building_information(self):
        """Test building information enums."""
        enum_dbhandler = DBEnumHandler()
        # building types
        result = enum_dbhandler.get_building_types()
        assert result.name == 'IfcBuilding'
        assert result.label == 'BuildingType'
        assert len(result.children) > 1
        educational = result.get_son('EducationalBuilding')
        assert educational is not None
        assert len(educational.children) == 3
        # floor types
        floor = enum_dbhandler.get_floor_types()
        assert floor.name == 'Floor'
        assert floor.label == 'Floor'
        assert len(floor.children) == 2
        subterranean = result.get_son('Subterranean')
        assert subterranean is None
        subterranean = floor.get_son('Subterranean')
        assert subterranean is not None
        assert len(subterranean.children) == 0
        ground = floor.get_son('Ground')
        assert ground is not None
        assert len(ground.children) == 0
        # space types
        result = enum_dbhandler.get_space_types()
        assert result.name == 'IfcSpace'
        assert result.label == 'Space'
        assert len(result.children) > 1
        # covering types
        result = enum_dbhandler.get_window_covering_types()
        assert result.name == 'WindowCoveringType'
        assert result.label == 'WindowCovering'
        assert len(result.children) == 4

    def test_db_enums_geographical_information(self):
        """Test geographical information enums."""
        enum_dbhandler = DBEnumHandler()
        # orientation types
        result = enum_dbhandler.get_orientation_types()
        assert result.name == 'Orientation'
        assert result.label == 'Orientation'
        assert len(result.children) == 8
        # hemisphere types
        result = enum_dbhandler.get_hemisphere_types()
        assert result.name == 'Hemisphere'
        assert result.label == 'Hemisphere'
        assert len(result.children) == 2
        # climate types
        result = enum_dbhandler.get_climate_types()
        assert result.name == 'Climate'
        assert result.label == 'Climate'
        assert len(result.children) == 5

    def test_db_enums_occupancy_information(self):
        """Test occupancy information enums."""
        enum_dbhandler = DBEnumHandler()
        # gender types
        result = enum_dbhandler.get_gender_types()
        assert result.name == 'Gender'
        assert result.label == 'Gender'
        assert len(result.children) == 2

        # TODO: age categories

        # occupant states
        # result = enum_dbhandler.get_occupant_states()
        # assert result.name == 'OccupantStateProperties'
        # assert result.label == 'OccupantState'
        # TODO: fix ontology
        # assert len(result.children) == 2

    def test_db_enums_energy(self):
        """Test occupancy information enums."""
        enum_dbhandler = DBEnumHandler()
        # get energy sources
        result = enum_dbhandler.get_energy_sources()
        assert len(result.children) == 2
        # get renewable energy sources
        result = enum_dbhandler.get_renewable_energy_sources()
        assert len(result.children) == 9

    def test_db_enums_observation_types(self):
        enum_dbhandler = DBEnumHandler()
        result = enum_dbhandler.get_observation_types()
        assert len(result.children) > 0

    def test_db_enums_medium_types(self):
        enum_dbhandler = DBEnumHandler()
        result = enum_dbhandler.get_medium_types()
        assert len(result.children) > 0

    def test_db_enums_measure_units(self):
        enum_dbhandler = DBEnumHandler()
        # get all units
        result = enum_dbhandler.get_units()
        assert len(result.children) > 0
        # temperature units
        result = enum_dbhandler.get_temperature_units()
        assert result.name == 'TemperatureUnit'
        assert result.label == 'TemperatureUnit'
        assert len(result.children) > 0
        # humidity units
        result = enum_dbhandler.get_humidity_units()
        assert result.name == 'HumidityUnit'
        assert result.label == 'HumidityUnit'
        # assert len(result.children) > 0
        # pressure units
        result = enum_dbhandler.get_pressure_units()
        assert result.name == 'PressureOrStressUnit'
        assert result.label == 'PressureUnit'
        assert len(result.children) > 0
        # length units
        result = enum_dbhandler.get_length_units()
        assert result.name == 'LengthUnit'
        assert result.label == 'LengthUnit'
        assert len(result.children) > 0
        # flow units
        result = enum_dbhandler.get_flow_units()
        assert result.name == 'VolumePerTimeUnit'
        assert result.label == 'FlowUnit'
        assert len(result.children) > 0
        # distance units
        result = enum_dbhandler.get_distance_units()
        assert result.name == 'AreaUnit'
        assert result.label == 'AreaUnit'
        assert len(result.children) > 0
        # volume units
        result = enum_dbhandler.get_volume_units()
        assert result.name == 'VolumeUnit'
        assert result.label == 'VolumeUnit'
        assert len(result.children) > 0
        # radiance units
        result = enum_dbhandler.get_radiance_units()
        assert result.name == 'RadianceUnit'
        assert result.label == 'RadianceUnit'
        # assert len(result.children) > 0
        # power units
        result = enum_dbhandler.get_power_units()
        assert result.name == 'PowerUnit'
        assert result.label == 'PowerUnit'
        # assert len(result.children) > 0
        # electric current units
        result = enum_dbhandler.get_electric_current_units()
        assert result.name == 'ElectricCurrentUnit'
        assert result.label == 'ElectricCurrentUnit'
        # assert len(result.children) > 0
        # electric charge units
        result = enum_dbhandler.get_electric_charge_units()
        assert result.name == 'ElectricChargeUnit'
        assert result.label == 'ElectricChargeUnit'
        # assert len(result.children) > 0
