"""Tests the interface Building/DB"""

import pytest
from marshmallow import ValidationError

from bemserver.database import BuildingDB
from bemserver.database.utils import generate_id
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Building

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestBuildingDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle buildings in the ontology."""

    def test_db_building_get_empty(self):

        building_db = BuildingDB()

        # get all items
        result = building_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            building_db.get_by_id('not_existing')

    def test_db_building_create(self, init_sites):

        site_ids = init_sites
        building_db = BuildingDB()

        # check that database is empty
        result = building_db.get_all()
        assert list(result) == []

        # create an item
        building = Building(
            'Building #0', 'BarRestaurant', site_ids[0], area=666)
        new_building_id = building_db.create(building)
        assert new_building_id is not None
        assert new_building_id == building.id

        # check that database is not empty now
        result = building_db.get_all()
        buildings = list(result)
        assert len(buildings) == 1
        assert buildings[0].id == building.id
        assert buildings[0].name == building.name
        assert buildings[0].description == building.description
        assert buildings[0].area == building.area
        assert buildings[0].site_id == building.site_id == site_ids[0]

        # error: invalid site
        # TODO: test this at `Thing` level ?
        building.site_id = generate_id()
        with pytest.raises(ValidationError) as exc:
            building_db.update(building.id, building)
        assert 'site_id' in exc.value.messages

    def test_db_building_select_filter(self, init_sites):
        site_ids = init_sites
        building_db = BuildingDB()

        # create an item
        building = Building(
            'Building #0', 'BarRestaurant', site_ids[0], area=666)
        new_building_id = building_db.create(building)

        # check that database is empty
        result = building_db.get_all(site_id=str(site_ids[0]))
        buildings = list(result)
        assert len(buildings) == 1
        assert buildings[0].id == new_building_id

        result = building_db.get_all(kind='CommercialBuilding')
        buildings = list(result)
        assert len(buildings) == 1
        assert buildings[0].id == new_building_id

    def test_db_building_update_delete(self, init_buildings):

        building_ids, _ = init_buildings
        building_db = BuildingDB()

        # get all items
        result = building_db.get_all()
        buildings = list(result)
        assert len(buildings) == 2
        for cur_building in buildings:
            assert cur_building.id in building_ids

        # get an item by its ID
        building = building_db.get_by_id(buildings[0].id)

        # update item data
        new_description = 'updated by patator'
        new_area = 999
        building.description = new_description
        building.area = new_area
        building_db.update(building.id, building)

        # check that item has really been updated in database
        updated_building = building_db.get_by_id(building.id)
        assert updated_building.id == building.id
        assert updated_building.name == building.name
        assert updated_building.description == new_description
        assert updated_building.area == new_area
        assert updated_building.site_id == building.site_id

        # delete an item by its ID
        building_db.remove(building.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            building_db.get_by_id(building.id)
