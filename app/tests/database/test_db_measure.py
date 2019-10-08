"""Tests the interface Measure/DB"""

import pytest

from bemserver.database import MeasureDB, SensorDB, SpaceDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Measure, MeasureValueProperties

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestMeasureDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle measures in the ontology."""

    def test_db_measure_get_empty(self):

        measure_db = MeasureDB()

        # get all items
        result = measure_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            measure_db.get_by_id('not_existing')

    def test_db_measure_create(self, init_sensors):

        sensor_ids, space_ids, _, _, _ = init_sensors
        sensor_id = sensor_ids[0]
        measure_db = MeasureDB()

        # check that database is empty
        result = measure_db.get_all()
        assert list(result) == []

        # create an item
        measure = Measure(
            sensor_id, 'DegreeCelsius', 'Air', 'Temperature',
            description='A sample measure', outdoor=True, set_point=True,
            ambient=True, associated_locations=space_ids)
        new_measure_id = measure_db.create(measure)
        assert new_measure_id is not None
        assert new_measure_id == measure.id

        # check that database is not empty now
        result = measure_db.get_all()
        measures = list(result)
        assert len(measures) == 1
        assert measures[0].id == measure.id
        assert measures[0].description == measure.description
        assert measures[0].medium == measure.medium
        assert measures[0].unit == measure.unit == 'DegreeCelsius'
        assert measures[0].observation_type == measure.observation_type
        assert measures[0].method == 'Frequency'
        assert not measures[0].on_index
        assert measures[0].set_point
        assert measures[0].outdoor
        assert measures[0].ambient
        assert measures[0].sensor_id == sensor_id
        assert {loc.type for loc in measures[0].associated_locations} ==\
            {'space', 'floor', 'building', 'site'}
        assert set(space_ids) ==\
            {loc.id for loc in measures[0].associated_locations if
             loc.type == 'space'}
        for loc_type in ['floor', 'building', 'site']:
            assert len([loc.id for loc in measures[0].associated_locations if
                        loc.type == loc_type]) == 1

        # check the link from sensor to measure is created
        sensor_db = SensorDB()
        sensor = sensor_db.get_by_id(sensor_id)
        assert new_measure_id in sensor.measures

        # assert set(measures[0].measures) == set(measure.measures)

    def test_db_measure_filter(self, init_sensors):
        sensor_ids, space_ids, _, building_ids, _ = init_sensors
        building_id = building_ids[0]
        measure_db = MeasureDB()

        # check that database is empty
        result = measure_db.get_all(building_id=building_id)
        assert list(result) == []
        result = measure_db.get_all(space_id=space_ids[0])
        assert list(result) == []

        # create an item
        measure_db.create(
            Measure(sensor_ids[0], 'DegreeCelsius', 'Air', 'Temperature',
                    associated_locations=[str(space_ids[0])],
                    description='New sample measure'))
        measure_db.create(
            Measure(sensor_ids[1], 'DegreeCelsius', 'Air', 'Temperature',
                    associated_locations=[
                        str(space_ids[1]), str(space_ids[0])],
                    description='New sample measure'))

        measures = list(measure_db.get_all(location_id=space_ids[0]))
        assert len(measures) == 2
        result = measure_db.get_all(location_id=space_ids[1])
        assert len(list(result)) == 1

        space_db = SpaceDB()
        # common site for the two spaces
        result = measure_db.get_all(
            location_id=space_db.get_parent(str(space_ids[0])))
        assert len(list(result)) == 2

    def test_db_measure_update(self, init_measures):

        measure_ids, _, _, _, building_ids, _ = init_measures
        measure_db = MeasureDB()

        # get all items
        result = measure_db.get_all()
        measures = list(result)
        assert len(measures) == 2
        for cur_measure in measures:
            assert cur_measure.id in measure_ids

        # get an item by its ID
        measure = measure_db.get_by_id(measures[0].id)
        old_sensor_id = measure.sensor_id
        old_locations = measure.associated_locations

        # update item data
        new_description = 'updated by patator'
        new_locations = [str(building_ids[0])]
        new_frequency = 12
        measure.description = new_description
        measure.associated_locations = new_locations
        measure.on_index = True
        material_pties = MeasureValueProperties(frequency=new_frequency)
        measure.value_properties = material_pties
        measure_db.update(measure.id, measure)

        # check that item has really been updated in database
        updated_measure = measure_db.get_by_id(measure.id)
        assert updated_measure.id == measure.id
        assert updated_measure.description == new_description
        for loc_type in ['building', 'site']:
            assert len([loc for loc in updated_measure.associated_locations
                        if loc.type == loc_type]) == 1
        for loc_type in ['space', 'floor']:
            assert len([loc for loc in updated_measure.associated_locations
                        if loc.type == loc_type]) == 0
        assert [loc.id for loc in updated_measure.associated_locations
                if loc.type == 'building'] == [building_ids[0]]
        assert updated_measure.on_index
        assert updated_measure.sensor_id == old_sensor_id
        assert set(updated_measure.associated_locations) != set(old_locations)
        assert updated_measure.value_properties.frequency == new_frequency

        # delete an item by its ID
        measure_db.remove(measure.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            measure_db.get_by_id(measure.id)
