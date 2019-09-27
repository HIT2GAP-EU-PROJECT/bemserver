"""Tests the interface Floor/DB"""

import pytest

from bemserver.database import FloorDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Floor

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestFloorDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle floors in the ontology."""

    def test_db_floor_get_empty(self):

        floor_db = FloorDB()

        # get all items
        result = floor_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            floor_db.get_by_id('not_existing')

    def test_db_floor_create(self, init_buildings):

        building_ids, _ = init_buildings
        floor_db = FloorDB()

        # check that database is empty
        result = floor_db.get_all()
        assert list(result) == []

        # create an item
        floor = Floor('Floor #0', 1, building_ids[0], 'Floor')
        new_floor_id = floor_db.create(floor)
        assert new_floor_id is not None
        assert new_floor_id == floor.id

        # check that database is not empty now
        result = floor_db.get_all()
        floors = list(result)
        assert len(floors) == 1
        assert floors[0].id == floor.id
        assert floors[0].name == floor.name
        assert floors[0].description == floor.description
        assert floors[0].level == floor.level
        assert floors[0].kind == floor.kind
        assert floors[0].building_id == floor.building_id == building_ids[0]

    def test_db_floor_update_delete(self, init_floors):

        floor_ids, building_ids, _ = init_floors
        building_id = building_ids[0]
        floor_db = FloorDB()

        # get all items
        result = floor_db.get_all()
        floors = list(result)
        assert len(floors) == 2
        for cur_floor in floors:
            assert cur_floor.id in floor_ids

        # get an item by its ID
        floor = floor_db.get_by_id(floors[0].id)

        # update item data
        new_description = 'updated by patator'
        new_level = 7
        floor.description = new_description
        floor.level = new_level
        floor_db.update(floor.id, floor)

        # check that item has really been updated in database
        updated_floor = floor_db.get_by_id(floor.id)
        assert updated_floor.id == floor.id
        assert updated_floor.name == floor.name
        assert updated_floor.description == new_description
        assert updated_floor.level == new_level
        assert updated_floor.kind == floor.kind
        assert updated_floor.building_id == floor.building_id == building_id

        # delete an item by its ID
        floor_db.remove(floor.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            floor_db.get_by_id(floor.id)
