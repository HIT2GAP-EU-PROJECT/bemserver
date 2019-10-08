"""Tests for api floors views"""

import pytest

from bemserver.api.extensions.database import db_accessor as dba
from bemserver.models import Floor

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen, get_dictionary_no_none
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsFloors(TestCoreApi):
    """Floor api views tests"""

    base_uri = '/floors/'

    def test_views_floors_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True}], indirect=True)
    def test_views_floors_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get list: 4 found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get list with a filter: 2 found
        response = self.get_items(kind='Ground')
        assert response.status_code == 200
        assert len(response.json) == 2

    @pytest.mark.xfail
    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True}], indirect=True)
    def test_views_floors_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get list:
        # sorting by name descending
        response = self.get_items(sort='-name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'floor_D'
        assert response.json[1]['name'] == 'floor_C'
        assert response.json[2]['name'] == 'floor_B'
        assert response.json[3]['name'] == 'floor_A'

        # sorting by name ascending
        response = self.get_items(sort='name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'floor_A'
        assert response.json[1]['name'] == 'floor_B'
        assert response.json[2]['name'] == 'floor_C'
        assert response.json[3]['name'] == 'floor_D'

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True}], indirect=True)
    def test_views_floors_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        floor_id = str(init_db_data['floors'][0])

        # Get by its ID
        response = self.get_item_by_id(item_id=floor_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=floor_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    def test_views_floors_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        building_id = str(init_db_data['buildings'][0])

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new item
        response = self.post_item(
            name='A floor', kind='Floor', level=69,
            spatial_info={'area': 42, 'max_height': 2.4},
            description='A top level floor !', building_id=building_id)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'A floor'
        assert response.json['kind'] == 'Floor'
        assert response.json['level'] == 69
        assert response.json['spatial_info']['area'] == 42
        assert response.json['spatial_info']['max_height'] == 2.4
        assert response.json['description'] == 'A top level floor !'
        assert response.json['building_id'] == building_id

        # Get list: 1 found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

        # Errors:
        # wrong kind (422)
        response = self.post_item(
            name='wrong_kind', kind='wrong', level=0,
            spatial_info={'area': 0, 'max_height': 0},
            building_id=building_id)
        assert response.status_code == 422
        assert 'kind' in response.json['errors']

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only', kind='Floor', level=0,
            spatial_info={'area': 0, 'max_height': 0},
            building_id=building_id)
        assert response.status_code == 201
        assert response.json['id'] != new_id

    @pytest.mark.parametrize('init_db_data', [
        {'gen_sites': True, 'gen_buildings': True, 'gen_floors': True}
        ], indirect=True)
    def test_views_floors_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        floor_id = str(init_db_data['floors'][0])

        floor_json = self.get_item_by_id(item_id=floor_id)
        building_id = str(floor_json.json['building_id'])
        assert floor_json.status_code == 200
        # get etag value
        etag_value = floor_json.headers.get('etag', None)

        spatial_info = get_dictionary_no_none(floor_json.json['spatial_info'])

        # Update...
        f_name_updated = 'An updated floor name'
        response = self.put_item(
            item_id=floor_id, name=f_name_updated,
            kind=floor_json.json['kind'], level=floor_json.json['level'],
            building_id=building_id, spatial_info=spatial_info,
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == f_name_updated
        assert response.json['kind'] == floor_json.json['kind']
        assert response.json['level'] == floor_json.json['level']
        assert response.json['spatial_info'] == floor_json.json['spatial_info']
        assert 'description' not in response.json
        assert response.json['building_id'] == str(building_id)

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True}], indirect=True)
    def test_views_floors_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        floor_id = str(init_db_data['floors'][0])

        # get etag value
        response = self.get_item_by_id(item_id=floor_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete...
        response = self.delete_item(
            item_id=floor_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Item is really deleted: not found (404)
        response = self.get_item_by_id(item_id=floor_id)
        assert response.status_code == 404

    def test_views_floors_types(self):
        """Test get_list floor types api endpoint"""

        # Get floor types
        kwargs = {'uri': '{}types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get floor types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsFloorsPermissions(TestCoreApiAuthCert):
    """Floors api views tests, with authentication"""

    base_uri = '/floors/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_floors': True}], indirect=True)
    def test_views_floors_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 floors in DB, but user 'multi-site' is only allowed
        #  to list floors for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        floor_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for floor in response.json:
            site_id = dba.get_parent(Floor, floor['id'])
            assert uacc.verify_scope(sites=[site_id])

        allowed_floor_id = str(floor_data['id'])
        not_allowed_floor_id = str(db_data['floors'][-1])
        allowed_building_id = str(floor_data['building_id'])
        not_allowed_building_id = str(db_data['buildings'][-1])

        # GET:
        # allowed floor (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_floor_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed floor (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_floor_id)
        assert response.status_code == 403

        # POST:
        # user role is allowed to post a new floor on allowed site
        response = self.post_item(
            headers=auth_header,
            name='New floor', kind='Floor', level=69,
            spatial_info={'area': 42, 'max_height': 2.4},
            building_id=allowed_building_id)
        assert response.status_code == 201
        # not allowed
        response = self.post_item(
            headers=auth_header,
            name='New building 2', kind='Floor', level=69,
            spatial_info={'area': 42, 'max_height': 2.4},
            building_id=not_allowed_building_id)
        assert response.status_code == 403

        # an allowed floor has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        # UPDATE:
        # allowed floor (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_floor_id,
            name='Updated-name', kind='Floor', level=69,
            spatial_info={'area': 42, 'max_height': 2.4},
            building_id=allowed_building_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed floor (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_floor_id,
            name='Updated-name', kind='Floor', level=69,
            spatial_info={'area': 42, 'max_height': 2.4},
            building_id=not_allowed_building_id)
        assert response.status_code == 403

        # DELETE:
        # allowed floor (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=allowed_floor_id)
        assert response.status_code == 204
        # not allowed floor (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_floor_id)
        assert response.status_code == 403

        # an allowed floor has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
