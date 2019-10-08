"""Tests for api slabs views"""

import pytest

from bemserver.api.extensions.database import db_accessor as dba
from bemserver.models import Building

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen, get_dictionary_no_none
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsSlabs(TestCoreApi):
    """Slab api views tests"""

    base_uri = '/slabs/'

    def test_views_slabs_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_floors': True, 'gen_slabs': True}],
        indirect=True)
    def test_views_slabs_get_list_filter(self):
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
        response = self.get_items(name='slab_C')
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_floors': True, 'gen_slabs': True}],
        indirect=True)
    def test_views_slabs_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        slab_id = str(init_db_data['slabs'][0])

        # Get by its ID
        response = self.get_item_by_id(item_id=slab_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=slab_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': True, 'gen_floors': True}
        ], indirect=True)
    def test_views_slabs_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        building_id = str(init_db_data['buildings'][0])

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        #  Post a new item
        f_floors = [str(init_db_data['floors'][0]),
                    str(init_db_data['floors'][1])]
        response = self.post_item(
            name='Magical slab', floors=f_floors, surface_info={'area': 42},
            description='It can disappear...', building_id=building_id)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'Magical slab'
        assert response.json['floors'] == f_floors
        assert response.json['surface_info']['area'] == 42
        assert response.json['description'] == 'It can disappear...'
        assert 'kind' not in response.json
        assert response.json['building_id'] == building_id
        assert response.json['windows'] == []

        #  Get list: 1 found
        slab_json = self.get_items()
        assert slab_json.status_code == 200
        assert len(slab_json.json) == 1

        # Errors:
        # wrong spatial info (422)
        response = self.post_item(
            name='wrong_spatial', surface_info='wrong',
            floors=[str(init_db_data['floors'][2])],
            building_id=str(init_db_data['buildings'][3]))
        assert response.status_code == 422

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only',
            floors=[str(init_db_data['floors'][0])],
            surface_info={'area': 0},
            building_id=str(init_db_data['buildings'][0]))
        assert response.status_code == 201
        assert response.json['id'] != new_id

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_slabs': True}
        ], indirect=True)
    def test_views_slabs_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        slab_id = str(init_db_data['slabs'][0])

        slab_json = self.get_item_by_id(item_id=slab_id)
        building_id = str(slab_json.json['building_id'])
        assert slab_json.status_code == 200

        # get etag value
        etag_value = slab_json.headers.get('etag', None)

        surface_info = get_dictionary_no_none(slab_json.json['surface_info'])

        # Update...
        f_name_updated = 'An updated slab name'
        response = self.put_item(
            item_id=slab_id, name=f_name_updated,
            floors=slab_json.json['floors'],
            surface_info=surface_info, building_id=building_id,
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == f_name_updated
        assert set(response.json['floors']) == set(slab_json.json['floors'])
        assert 'description' not in response.json
        assert response.json['surface_info'] == slab_json.json['surface_info']
        assert response.json['building_id'] ==\
            str(slab_json.json['building_id'])

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_slabs': True}
        ], indirect=True)
    def test_views_slabs_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        slab_id = str(init_db_data['slabs'][0])

        # get etag value
        response = self.get_item_by_id(item_id=slab_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        #  Delete...
        response = self.delete_item(
            item_id=slab_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Item is really deleted: not found (404)
        response = self.get_item_by_id(item_id=slab_id)
        assert response.status_code == 404


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsSlabsPermissions(TestCoreApiAuthCert):
    """Slabs api views tests, with authentication"""

    base_uri = '/slabs/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_zones': True,
         'gen_slabs': True}
        ], indirect=True)
    def test_views_slabs_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 slabs in DB, but user 'multi-site' is only allowed
        #  to list slabs for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        slab_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for slab in response.json:
            site_id = dba.get_parent(Building, slab['building_id'])
            assert uacc.verify_scope(sites=[site_id])

        not_allowed_slab_id = str(db_data['slabs'][-1])
        allowed_building_id = str(slab_data['building_id'])
        not_allowed_building_id = str(db_data['buildings'][-1])

        # POST:
        # user role is allowed to post a new slab on allowed site
        response = self.post_item(
            headers=auth_header, name='New slab', kind='Roof', floors=[],
            surface_info={'area': 51}, building_id=allowed_building_id)
        assert response.status_code == 201
        slab_data = response.json
        allowed_slab_id = str(slab_data['id'])
        # not allowed
        response = self.post_item(
            headers=auth_header, name='New slab 2', kind='Roof', floors=[],
            surface_info={'area': 51}, building_id=not_allowed_building_id)
        assert response.status_code == 403

        # an allowed slab has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        # GET:
        # allowed slab (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_slab_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed slab (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_slab_id)
        assert response.status_code == 403

        # UPDATE:
        # allowed slab (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_slab_id,
            name='Updated-name', kind=slab_data['kind'],
            floors=slab_data['floors'], surface_info=slab_data['surface_info'],
            building_id=allowed_building_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed slab (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_slab_id,
            name='Updated-name', kind=slab_data['kind'],
            floors=slab_data['floors'], surface_info=slab_data['surface_info'],
            building_id=not_allowed_building_id)
        assert response.status_code == 403

        # DELETE:
        # allowed slab (in fact parent site)
        response = self.delete_item(headers=headers, item_id=allowed_slab_id)
        assert response.status_code == 204
        # not allowed slab (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_slab_id)
        assert response.status_code == 403

        # an allowed slab has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
