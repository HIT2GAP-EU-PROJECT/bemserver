"""Tests the interface Zone/DB"""

import pytest
from bemserver.database import ZoneDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Zone

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestZoneDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle zones in the ontology."""

    def test_db_zone_get_empty(self):

        zone_db = ZoneDB()

        # get all items
        result = zone_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            zone_db.get_by_id('not_existing')

    def test_db_zone_create(self, init_spaces):

        space_ids, _, building_ids, _ = init_spaces
        zone_db = ZoneDB()

        # check that database is empty
        result = zone_db.get_all()
        assert list(result) == []

        # create an item
        zone = Zone('Zone #0', [], space_ids, building_ids[0])
        new_zone_id = zone_db.create(zone)
        assert new_zone_id is not None
        assert new_zone_id == zone.id

        # check that database is not empty now
        result = zone_db.get_all()
        zones = list(result)
        assert len(zones) == 1
        assert zones[0].id == zone.id
        assert zones[0].name == zone.name
        assert zones[0].description == zone.description
        for space_id in zones[0].spaces:
            assert space_id in zone.spaces
        for space_id in zone.spaces:
            assert space_id in zones[0].spaces
        # TODO: test should be similar than for spaces
        assert zones[0].zones == zone.zones
        assert zones[0].building_id == zone.building_id

    def test_db_zone_update_delete(self, init_zones):

        zone_ids, _, _, _, _ = init_zones
        zone_db = ZoneDB()

        # get all items
        result = zone_db.get_all()
        zones = list(result)
        assert len(zones) == 2
        for cur_zone in zones:
            assert cur_zone.id in zone_ids

        # get an item by its ID
        zone = zone_db.get_by_id(zones[0].id)

        # update item data
        new_description = 'updated by patator'
        zone.description = new_description
        zone_db.update(zone.id, zone)

        # check that item has really been updated in database
        updated_zone = zone_db.get_by_id(zone.id)
        assert updated_zone.id == zone.id
        assert updated_zone.name == zone.name
        assert updated_zone.description == new_description
        assert set(updated_zone.spaces) == set(zone.spaces)
        assert set(updated_zone.zones) == set(zone.zones)
        assert updated_zone.building_id == zone.building_id

        # delete an item by its ID
        zone_db.remove(zone.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            zone_db.get_by_id(zone.id)
