"""Tests for IFC import data"""

import pytest

from bemserver.basicservices.bim.ifc_import import IfcImport
from bemserver.models import (
    Site, Building, Floor, Space, Zone, Facade, Window)

from tests import TestCoreBasicServices


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestBasicServicesIfcImport(TestCoreBasicServices):
    """IFC data import basic service tests"""

    def test_basic_services_ifc_import(self, ifc_filepath, db_accessor):
        """Test on IFC importation"""

        ifc_import = IfcImport(ifc_filepath, db_accessor=db_accessor)
        ifc_import.execute()

        # for cur_log_header, cur_log_time, cur_log_message in
        # ifc_import.report:
        #     print('{}\t{}\t{}'.format(
        #         cur_log_header, cur_log_time, cur_log_message))

        db_sites = db_accessor.get_list(Site)
        assert len(db_sites) == 1
        print(db_sites[0])

        db_buildings = db_accessor.get_list(Building)
        assert len(db_buildings) == 1
        assert db_buildings[0].name == 'The House'
        assert db_buildings[0].site_id == db_sites[0].id
        print(db_buildings[0])

        db_floors = db_accessor.get_list(Floor)
        assert len(db_floors) == 1
        assert db_floors[0].name == 'Level 0'
        assert db_floors[0].level == 0
        assert db_floors[0].building_id == db_buildings[0].id
        print(db_floors[0])

        db_spaces = db_accessor.get_list(Space)
        assert len(db_spaces) == 5
        for space in db_spaces:
            assert space.floor_id == db_floors[0].id
            assert space.spatial_info is not None
            print(space)

        db_zones = db_accessor.get_list(Zone)
        assert len(db_zones) == 0

        db_facades = db_accessor.get_list(Facade)
        assert len(db_facades) == 12
        for facade in db_facades:
            assert not facade.interior
            assert facade.surface_info.area is not None
            print(facade)

        db_windows = db_accessor.get_list(Window)
        assert len(db_windows) == 0
