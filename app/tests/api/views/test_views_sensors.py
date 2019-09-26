"""Tests for api sensor views"""

import pytest

from bemserver.api.extensions.database import db_accessor as dba
from bemserver.models import Sensor

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsSensors(TestCoreApi):
    """Sensor api views tests"""

    base_uri = '/sensors/'

    def test_views_sensors_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get sensor list: no sensors
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_sensors': True}], indirect=True)
    def test_views_sensors_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get sensor list: 4 sensors found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get sensor list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get sensor list with a filter: 2 sensors found
        response = self.get_items(name='sensor_A')
        assert response.status_code == 200
        assert len(response.json) == 1

        # Get sensor list with a filter: 2 sensors found
        # response = self.get_items(static=False)
        # assert response.status_code == 200
        # assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_sensors': True}], indirect=True)
    def test_views_sensors_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        sensor_id = str(init_db_data['sensors'][0])

        # Get sensor by its ID
        response = self.get_item_by_id(item_id=sensor_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get sensor by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=sensor_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_buildings': True}], indirect=True)
    def test_views_sensors_post(self, init_db_data):
        """Test post api endpoint"""

        # Get sensor list: no Sensors
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post sensor 1
        response = self.post_item(
            name='New sensor', description='Mock sensor #1',
            static=False,
            localization={'building_id': str(init_db_data['buildings'][0])}
        )
        assert response.status_code == 201
        assert response.json['name'] == 'New sensor'
        assert response.json['description'] == 'Mock sensor #1'
        assert response.json['static'] is False
        assert response.json['localization']['building_id'] == \
            str(init_db_data['buildings'][0])

        # Post sensor 2
        response = self.post_item(
            name='New sensor',
            description='Mock sensor #2',
            localization={'building_id': str(init_db_data['buildings'][0])}
        )
        assert response.status_code == 201
        assert response.json['name'] == 'New sensor'
        assert response.json['description'] == 'Mock sensor #2'
        assert response.json['static'] is True
        assert response.json['localization']['building_id'] == \
            str(init_db_data['buildings'][0])

        # Get sensor list: four sensor found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 2

        # Errors:
        # no system, no localization (422)
        # XXX: capture exception and send back HHTP error
        # response = self.post_item(
        #     name='New sensor', description='Mock sensor #3')
        # assert response.status_code == 422

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only',
            system_kind='electrical_communication_appliance_network',
            localization={'building_id': str(init_db_data['buildings'][0])})
        assert response.status_code == 201
        assert response.json['id'] != new_id

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_sensors': True, 'gen_measures': True}],
        indirect=True)
    def test_views_sensors_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        sensor_id = str(init_db_data['sensors'][0])

        # get etag value
        response = self.get_item_by_id(item_id=sensor_id)
        measure_ids = response.json['measures']
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Update sensor...
        static_update = False
        localization_update = {'site_id': str(init_db_data['sites'][1])}
        response = self.put_item(
            item_id=sensor_id, name=response.json['name'],
            description=response.json['description'],
            static=static_update, localization=localization_update,
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == response.json['name']
        assert response.json['description'] == response.json['description']
        assert response.json['static'] == static_update
        assert response.json['localization']['site_id'] ==\
            localization_update['site_id']
        assert measure_ids == response.json['measures']

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_sensors': True}], indirect=True)
    def test_views_sensors_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        sensor_id = str(init_db_data['sensors'][0])

        # get etag value
        response = self.get_item_by_id(item_id=sensor_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a sensor...
        response = self.delete_item(
            item_id=sensor_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Sensor is really deleted: not found (404)
        response = self.get_item_by_id(item_id=sensor_id)
        assert response.status_code == 404


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsSensorsPermissions(TestCoreApiAuthCert):
    """Sensors api views tests, with authentication"""

    base_uri = '/sensors/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True}], indirect=True)
    def test_views_sensors_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 sensors in DB, but user 'multi-site' is only allowed
        #  to list sensors for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        sensor_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for sensor in response.json:
            site_id = dba.get_parent(Sensor, sensor['id'])
            assert uacc.verify_scope(sites=[site_id])

        allowed_sensor_id = str(sensor_data['id'])
        not_allowed_sensor_id = str(db_data['sensors'][-1])
        allowed_site_id = str(db_data['sites'][0])
        not_allowed_site_id = str(db_data['sites'][-1])

        # GET:
        # allowed sensor (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_sensor_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed sensor (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_sensor_id)
        assert response.status_code == 403

        # POST:
        # user role is allowed to post a new sensor on allowed site
        response = self.post_item(
            headers=auth_header,
            name='New sensor', static=False,
            localization={'building_id': allowed_site_id})
        assert response.status_code == 201
        # not allowed
        response = self.post_item(
            headers=auth_header,
            name='New sensor 2', static=False,
            localization={'building_id': not_allowed_site_id})
        assert response.status_code == 403

        # an allowed sensor has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        # UPDATE:
        # allowed sensor (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_sensor_id,
            name='Updated-name', static=sensor_data['static'],
            localization=sensor_data['localization'])
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed sensor (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_sensor_id,
            name='Updated-name', static=sensor_data['static'],
            localization=sensor_data['localization'])
        assert response.status_code == 403

        # DELETE:
        # allowed sensor (in fact parent site)
        response = self.delete_item(headers=headers, item_id=allowed_sensor_id)
        assert response.status_code == 204
        # not allowed sensor (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_sensor_id)
        assert response.status_code == 403

        # an allowed sensor has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
