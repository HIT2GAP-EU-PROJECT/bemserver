"""Tests the interface Sensor/DB"""

import pytest

from bemserver.database import SensorDB, SiteDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Sensor, Localization

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestSensorDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle sensors in the ontology."""

    def test_db_sensor_get_empty(self):

        sensor_db = SensorDB()

        # get all items
        result = sensor_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            sensor_db.get_by_id('not_existing')

    def _check_equal_localization(self, loc1, loc2):
        # ensure both localizations have a common element
        if loc1.site_id and loc2.site_id:
            assert loc1.site_id == loc2.site_id
        if loc1.building_id and loc2.building_id:
            assert loc1.building_id == loc2.building_id
        if loc1.floor_id and loc2.floor_id:
            assert loc1.floor_id == loc2.floor_id
        if loc1.space_id and loc2.space_id:
            assert loc1.space_id == loc2.space_id

    def test_db_sensor_create(self, init_spaces):

        space_ids, _, _, _ = init_spaces
        sensor_db = SensorDB()

        # check that database is empty
        result = sensor_db.get_all()
        assert list(result) == []

        # create an item

        sensor = Sensor('Sensor #0',
                        localization=Localization(space_id=space_ids[0]),
                        description='New sample sensor')
        new_sensor_id = sensor_db.create(sensor)
        assert new_sensor_id is not None
        assert new_sensor_id == sensor.id

        # check that database is not empty now
        result = sensor_db.get_all()
        sensors = list(result)
        assert len(sensors) == 1
        assert sensors[0].id == sensor.id
        assert sensors[0].name == sensor.name
        assert sensors[0].description == sensor.description
        self._check_equal_localization(sensors[0].localization,
                                       sensor.localization)
        assert sensors[0].static == sensor.static
        assert sensors[0].system_id == sensor.system_id
        assert set(sensors[0].measures) == set(sensor.measures)

        # ensure we can access the parent site
        sites = SiteDB().get_all()
        assert sensor_db.get_parent(sensor.id) in [
            str(site.id) for site in sites]

    def test_db_sensor_filter(self, init_spaces):
        space_ids, _, building_ids, _ = init_spaces
        sensor_db = SensorDB()

        # check that database is empty
        result = sensor_db.get_all(building_id=building_ids[0])
        assert list(result) == []
        result = sensor_db.get_all(space_id=space_ids[0])
        assert list(result) == []

        # create an item
        sensor_db.create(
            Sensor(
                'Sensor #0', localization=Localization(space_id=space_ids[0]),
                description='New sample sensor'))
        sensor_db.create(
            Sensor(
                'Sensor #1', localization=Localization(space_id=space_ids[1]),
                description='New sample sensor'))
        # result = sensor_db.get_all(building_id=building_id)
        # assert len(list(result)) == 2

        sensors = list(sensor_db.get_all(space_id=space_ids[0]))
        assert len(sensors) == 1
        result = sensor_db.get_all(space_id=space_ids[1])
        assert len(list(result)) == 1
        assert sensors[0].localization.site_id and \
            sensors[0].localization.building_id and \
            sensors[0].localization.floor_id and \
            sensors[0].localization.space_id

    def test_db_sensor_update(self, init_sensors):

        sensor_ids, _, _, building_ids, _ = init_sensors
        sensor_db = SensorDB()

        # get all items
        result = sensor_db.get_all()
        sensors = list(result)
        assert len(sensors) == 2
        for cur_sensor in sensors:
            assert cur_sensor.id in sensor_ids

        # get an item by its ID
        sensor = sensor_db.get_by_id(sensors[0].id)

        # update item data
        new_description = 'updated by patator'
        new_localization = Localization(building_id=building_ids[0])
        sensor.description = new_description
        sensor.localization = new_localization
        sensor.static = False
        sensor_db.update(sensor.id, sensor)

        # check that item has really been updated in database
        updated_sensor = sensor_db.get_by_id(sensor.id)
        assert updated_sensor.id == sensor.id
        assert updated_sensor.name == sensor.name
        assert updated_sensor.description == new_description
        self._check_equal_localization(
            updated_sensor.localization, new_localization)
        assert updated_sensor.system_id == sensor.system_id
        # TODO: to be changed
        assert set(updated_sensor.measures) == set(sensor.measures)
        assert updated_sensor.static == sensor.static

        # delete an item by its ID
        sensor_db.remove(sensor.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            sensor_db.get_by_id(sensor.id)
