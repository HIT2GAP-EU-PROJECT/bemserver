"""Tests for api measure views"""

import pytest

from bemserver.api.extensions.database import db_accessor as dba
from bemserver.models import Measure

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsMeasures(TestCoreApi):
    """Measure api views tests"""

    base_uri = '/measures/'

    subitems_uri = {
        'values': {
            'uri': '/values'
        }
    }

    def test_views_measures_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get measure list: no measures
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.parametrize(
        'init_db_data',
        [{'gen_buildings': True, 'gen_sensors': True, 'gen_measures': True}],
        indirect=True)
    def test_views_measures_get_list_filter(self, init_db_data):
        """Test get_list (with filter) api endpoint"""

        # retrieve database informations
        sensor_id = str(init_db_data['sensors'][0])
        space_id = str(init_db_data['spaces'][0])
        site_id = str(init_db_data['sites'][0])
        site_id_ko = str(init_db_data['sites'][1])

        # Get measure list: 4 measures found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get measure list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get measure list with a filter: 2 measure found
        response = self.get_items(observation_type='Temperature')
        assert response.status_code == 200
        assert len(response.json) == 4

        # Get measure list with a filter: 4 measures found
        response = self.get_items(sensor_id=sensor_id)
        assert response.status_code == 200
        assert len(response.json) == 4

        response = self.get_items(medium='Air')
        assert response.status_code == 200
        assert len(response.json) == 2

        response = self.get_items(location_id=space_id)
        assert response.status_code == 200
        assert len(response.json) == 1

        response = self.get_items(location_id=site_id)
        assert response.status_code == 200
        assert len(response.json) == 1

        response = self.get_items(location_id=site_id_ko)
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.xfail
    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize(
        'init_db_data',
        [{'gen_buildings': True, 'gen_sensors': True, 'gen_measures': True}],
        indirect=True)
    def test_views_measures_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get measures list:
        # sorting by name descending
        response = self.get_items(sort='-name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'measure_D'
        assert response.json[1]['name'] == 'measure_C'
        assert response.json[2]['name'] == 'measure_B'
        assert response.json[3]['name'] == 'measure_A'

        # sorting by name ascending
        response = self.get_items(sort='name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'measure_A'
        assert response.json[1]['name'] == 'measure_B'
        assert response.json[2]['name'] == 'measure_C'
        assert response.json[3]['name'] == 'measure_D'

    @pytest.mark.parametrize(
        'init_db_data',
        [{'gen_buildings': True, 'gen_sensors': True}],
        indirect=True)
    def test_views_measure_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        sensor_id = str(init_db_data['sensors'][0])
        building_id1 = str(init_db_data['buildings'][0])
        building_id2 = str(init_db_data['buildings'][1])

        # Get Measure list: no measures
        response = self.get_items()
        assert response.status_code == 200
        assert not response.json

        # Post a new measure
        response = self.post_item(
            sensor_id=sensor_id, description='test new measure!',
            observation_type='Energy', medium='Heat', outdoor=True,
            unit='Meter', on_index='true', set_point='true', external_id='id1',
            associated_locations=[building_id1, building_id2],
            value_properties={'vmin': -50, 'vmax': 50})
        # XXX: An energy measured in meters. No problem!
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['description'] == 'test new measure!'
        assert response.json['unit'] == 'Meter'
        assert response.json['observation_type'] == 'Energy'
        assert response.json['medium'] == 'Heat'
        assert response.json['value_properties']['vmin'] == -50
        assert response.json['value_properties']['vmax'] == 50
        location_ids = list(map(
            lambda x: x['id'], response.json['associated_locations']))
        assert building_id1 in location_ids
        assert building_id2 in location_ids

        response = self.post_item(
            sensor_id=sensor_id,
            # observation_type='Temperature', medium='Air',
            unit='DegreeCelsius', external_id='id2',
            value_properties={'vmin': -50, 'vmax': 50})
        assert response.status_code == 201
        measure_id = response.json['id']

        response = self.get_item_by_id(item_id=measure_id)
        assert response.status_code == 200

        # Get measure list: 2 measure found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 2

        # Get and test filters
        response = self.get_items(medium='Heat')
        assert response.status_code == 200
        assert len(response.json) == 1

        response = self.get_items(observation_type='Energy')
        assert response.status_code == 200
        assert len(response.json) == 1

        response = self.get_items(outdoor=True)
        assert response.status_code == 200
        assert len(response.json) == 1

        response = self.get_items(on_index='true')
        assert response.status_code == 200
        assert len(response.json) == 1

        response = self.get_items(set_point='true')
        assert response.status_code == 200
        assert len(response.json) == 1

        response = self.get_items(external_id='id1')
        assert response.status_code == 200
        assert len(response.json) == 1

        # Errors:
        # wrong measure_unit (422)
        response = self.post_item(
            sensor_id=sensor_id, name='wrong_kind_choice',
            measure_unit='wrong')
        assert response.status_code == 422
        # missing measure_unit (422)
        response = self.post_item(sensor_id=sensor_id, name='missing_kind')
        assert response.status_code == 422

    @pytest.mark.parametrize(
        'init_db_data',
        [{'gen_buildings': True, 'gen_sensors': True, 'gen_measures': True}],
        indirect=True)
    def test_views_measures_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        measure_id = str(init_db_data['measures'][0])
        building_id = str(init_db_data['buildings'][2])

        measure_json = self.get_item_by_id(item_id=measure_id)
        assert measure_json.status_code == 200
        sensor_id = str(measure_json.json['sensor_id'])

        # get etag value
        etag_value = measure_json.headers.get('etag', None)

        # Update...
        response = self.put_item(
            sensor_id=sensor_id, item_id=measure_id,
            description='test new measure!',
            value_properties={'vmin': 0, 'vmax': 0}, medium='Air',
            unit='DegreeFahrenheit', observation_type='Temperature',
            method='OnChange', outdoor=True, on_index=True, set_point=True,
            associated_locations=[building_id],
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['id'] is not None
        assert response.json['description'] == 'test new measure!'
        assert response.json['unit'] == 'DegreeFahrenheit'
        assert response.json['observation_type'] == 'Temperature'
        assert response.json['medium'] == 'Air'
        assert response.json['value_properties']['vmin'] == 0
        assert response.json['value_properties']['vmax'] == 0
        assert response.json['method'] == 'OnChange'
        assert response.json['outdoor']
        assert response.json['on_index']
        assert response.json['set_point']
        assert building_id in map(
            lambda x: x['id'], response.json['associated_locations'])

    @pytest.mark.parametrize(
        'init_db_data',
        [{'gen_buildings': True, 'gen_sensors': True, 'gen_measures': True}],
        indirect=True)
    def test_views_measures_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        measure_id = str(init_db_data['measures'][0])

        # get etag value
        response = self.get_item_by_id(item_id=measure_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a measure...
        response = self.delete_item(
            item_id=measure_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Resource is really deleted: not found (404)
        response = self.get_item_by_id(item_id=measure_id)
        assert response.status_code == 404

    def test_views_measures_observation_types(self):
        # Get observation types
        kwargs = {'uri': '{}observation_types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get observation types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_measures_medium_types(self):
        # Get medium types
        kwargs = {'uri': '{}medium_types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get medium types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_measures_units(self):
        # Get units
        kwargs = {'uri': '{}units/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get units with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsMeasuresPermissions(TestCoreApiAuthCert):
    """Measures api views tests, with authentication"""

    base_uri = '/measures/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_measures_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 measures in DB, but user 'multi-site' is only allowed
        #  to list measures for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        measure_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for measure in response.json:
            site_id = dba.get_parent(Measure, measure['id'])
            assert uacc.verify_scope(sites=[site_id])

        allowed_measure_id = str(measure_data['id'])
        not_allowed_measure_id = str(db_data['measures'][-1])
        allowed_sensor_id = str(measure_data['sensor_id'])
        not_allowed_sensor_id = str(db_data['sensors'][-1])

        # GET:
        # allowed measure (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_measure_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed measure (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_measure_id)
        assert response.status_code == 403

        # POST:
        # user role is allowed to post a new measure on allowed site
        response = self.post_item(
            headers=auth_header,
            name='New measure', observation_type='Temperature', medium='Air',
            unit='DegreeCelsius', value_properties={'vmin': -50, 'vmax': 50},
            sensor_id=allowed_sensor_id)
        assert response.status_code == 201
        # not allowed
        response = self.post_item(
            headers=auth_header,
            name='New sensor 2', observation_type='Temperature', medium='Air',
            unit='DegreeCelsius', value_properties={'vmin': -50, 'vmax': 50},
            sensor_id=not_allowed_sensor_id)
        assert response.status_code == 403

        # an allowed measure has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        # UPDATE:
        # allowed measure (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_measure_id,
            name='Updated-name', observation_type='Temperature', medium='Air',
            unit='DegreeCelsius', method='OnChange', outdoor=True,
            on_index=False, set_point=False, sensor_id=allowed_sensor_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed measure (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_measure_id,
            name='Updated-name', observation_type='Temperature', medium='Air',
            unit='DegreeCelsius', method='OnChange',
            sensor_id=not_allowed_sensor_id)
        assert response.status_code == 403

        # DELETE:
        # XXX: refresh etag value, update != get_item_by_id response...weird...
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_measure_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # allowed measure (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=allowed_measure_id)
        assert response.status_code == 204
        # not allowed measure (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_measure_id)
        assert response.status_code == 403

        # an allowed measure has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
