"""Tests for api facades views"""

import pytest

from bemserver.api.extensions.database import db_accessor as dba
from bemserver.models import Building

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen, get_dictionary_no_none
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsFacades(TestCoreApi):
    """Facade api views tests"""

    base_uri = '/facades/'

    def test_views_facades_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_facades': True}
        ], indirect=True)
    def test_views_facades_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get list: 4 found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get list with a filter: 1 found
        response = self.get_items(name='facade_C')
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.xfail
    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_facades': True}
        ], indirect=True)
    def test_views_facades_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get list:
        # sorting by name descending
        response = self.get_items(sort='-name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'facade_D'
        assert response.json[1]['name'] == 'facade_C'
        assert response.json[2]['name'] == 'facade_B'
        assert response.json[3]['name'] == 'facade_A'

        # sorting by name ascending
        response = self.get_items(sort='name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'facade_A'
        assert response.json[1]['name'] == 'facade_B'
        assert response.json[2]['name'] == 'facade_C'
        assert response.json[3]['name'] == 'facade_D'

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_facades': True}
        ], indirect=True)
    def test_views_facades_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        facade_id = str(init_db_data['facades'][0])

        # Get by its ID
        response = self.get_item_by_id(item_id=facade_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=facade_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': True, 'gen_floors': True, 'gen_spaces': True}
        ], indirect=True)
    def test_views_facades_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        building_id = str(init_db_data['buildings'][0])

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new item
        f_spaces = [str(init_db_data['spaces'][0]),
                    str(init_db_data['spaces'][1]),
                    str(init_db_data['spaces'][3])]
        response = self.post_item(
            name='Magical facade', distance_unit='metric', spaces=f_spaces,
            surface_info={'area': 42}, windows_wall_ratio=0.14,
            description='It can disappear...', orientation='East',
            building_id=building_id)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'Magical facade'
        assert response.json['spaces'] == f_spaces
        assert response.json['surface_info']['area'] == 42
        assert response.json['orientation'] == 'East'
        assert response.json['windows_wall_ratio'] == 0.14
        assert response.json['description'] == 'It can disappear...'
        assert response.json['building_id'] == building_id

        # Get list: 1 found
        facade_json = self.get_items()
        assert facade_json.status_code == 200
        assert len(facade_json.json) == 1

        # Errors:
        # wrong spatial info (422)
        response = self.post_item(
            name='wrong_spatial', surface_info='wrong', windows_wall_ratio=0,
            spaces=[str(init_db_data['spaces'][2])],
            building_id=str(init_db_data['buildings'][3]))
        assert response.status_code == 422
        # wrong windows_wall_ratio (422)
        response = self.post_item(
            name='wrong_windows_wall_ratio', spaces=[str(uuid_gen())],
            surface_info={'area': 0}, orientation='North',
            windows_wall_ratio=42,
            building_id=str(init_db_data['buildings'][3]))
        assert response.status_code == 422

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only',
            spaces=[str(init_db_data['spaces'][0])],
            surface_info={'area': 0}, orientation='North',
            windows_wall_ratio=0,
            building_id=str(init_db_data['buildings'][0]))
        assert response.status_code == 201
        assert response.json['id'] != new_id

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_facades': True}
        ], indirect=True)
    def test_views_facades_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        facade_id = str(init_db_data['facades'][0])

        facade_json = self.get_item_by_id(item_id=facade_id)
        building_id = str(facade_json.json['building_id'])
        assert facade_json.status_code == 200

        # get etag value
        etag_value = facade_json.headers.get('etag', None)

        surface_info = get_dictionary_no_none(facade_json.json['surface_info'])

        # Update...
        f_name_updated = 'An updated facade name'
        response = self.put_item(
            item_id=facade_id, name=f_name_updated,
            spaces=facade_json.json['spaces'],
            windows_wall_ratio=facade_json.json['windows_wall_ratio'],
            surface_info=surface_info, building_id=building_id,
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == f_name_updated
        assert set(response.json['spaces']) == set(facade_json.json['spaces'])
        assert (response.json['windows_wall_ratio'] ==
                facade_json.json['windows_wall_ratio'])
        assert 'description' not in response.json
        assert response.json['surface_info'] == (
            facade_json.json['surface_info'])
        assert response.json['building_id'] == str(
            facade_json.json['building_id'])

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_facades': True}
        ], indirect=True)
    def test_views_facades_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        facade_id = str(init_db_data['facades'][0])

        # get etag value
        response = self.get_item_by_id(item_id=facade_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete...
        response = self.delete_item(
            item_id=facade_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Item is really deleted: not found (404)
        response = self.get_item_by_id(item_id=facade_id)
        assert response.status_code == 404


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsFacadesPermissions(TestCoreApiAuthCert):
    """Facades api views tests, with authentication"""

    base_uri = '/facades/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_facades': True}
        ], indirect=True)
    def test_views_facades_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 facades in DB, but user 'multi-site' is only allowed
        #  to list facades for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        facade_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for facade in response.json:
            site_id = dba.get_parent(Building, facade['building_id'])
            assert uacc.verify_scope(sites=[site_id])

        allowed_facade_id = str(facade_data['id'])
        not_allowed_facade_id = str(db_data['facades'][-1])
        allowed_building_id = str(facade_data['building_id'])
        not_allowed_building_id = str(db_data['buildings'][-1])

        # GET:
        # allowed facade (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_facade_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed facade (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_facade_id)
        assert response.status_code == 403

        # POST:
        # user role is allowed to post a new facade on allowed site
        response = self.post_item(
            headers=auth_header,
            name='New facade', distance_unit='metric', spaces=[],
            surface_info={'area': 42}, windows_wall_ratio=0.14,
            orientation='East', building_id=allowed_building_id)
        assert response.status_code == 201
        # not allowed
        response = self.post_item(
            headers=auth_header,
            name='New facade 2', distance_unit='metric', spaces=[],
            surface_info={'area': 42}, windows_wall_ratio=0.14,
            orientation='East', building_id=not_allowed_building_id)
        assert response.status_code == 403

        # an allowed facade has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        # UPDATE:
        # allowed facade (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_facade_id,
            name='Updated-name', spaces=facade_data['spaces'],
            orientation='South_West', windows_wall_ratio=0.3,
            surface_info=facade_data['surface_info'],
            building_id=allowed_building_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed facade (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_facade_id,
            name='Updated-name', spaces=facade_data['spaces'],
            orientation='South_West', windows_wall_ratio=0.3,
            surface_info=facade_data['surface_info'],
            building_id=not_allowed_building_id)
        assert response.status_code == 403

        # DELETE:
        # allowed facade (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=allowed_facade_id)
        assert response.status_code == 204
        # not allowed facade (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_facade_id)
        assert response.status_code == 403

        # an allowed facade has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
