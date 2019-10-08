"""Tests for api space views"""

import pytest

from bemserver.api.extensions.database import db_accessor as dba
from bemserver.models import Space

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen, get_dictionary_no_none
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsSpaces(TestCoreApi):
    """Space api views tests"""

    base_uri = '/spaces/'

    def test_views_spaces_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True}], indirect=True)
    def test_views_spaces_get_list_filter(self, init_db_data):
        """Test get_list (with filter) api endpoint"""

        # retrieve database informations
        floor_id = str(init_db_data['floors'][0])

        # Get list: 4 found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get list with a filter: 2 found
        response = self.get_items(kind='Toilets')
        assert response.status_code == 200
        assert len(response.json) == 2

        # Get list with a filter: 4 found
        response = self.get_items(floor_id=floor_id)
        assert response.status_code == 200
        assert len(response.json) == 2

    @pytest.mark.xfail
    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True}], indirect=True)
    def test_views_spaces_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get list:
        # sorting by name descending
        response = self.get_items(sort='-name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'space_D'
        assert response.json[1]['name'] == 'space_C'
        assert response.json[2]['name'] == 'space_B'
        assert response.json[3]['name'] == 'space_A'

        # sorting by name ascending
        response = self.get_items(sort='name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'space_A'
        assert response.json[1]['name'] == 'space_B'
        assert response.json[2]['name'] == 'space_C'
        assert response.json[3]['name'] == 'space_D'

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True}], indirect=True)
    def test_views_spaces_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        space_id = str(init_db_data['spaces'][0])

        # Get by its ID
        response = self.get_item_by_id(item_id=space_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=space_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_floors': True}], indirect=True)
    def test_views_spaces_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        floor_id = str(init_db_data['floors'][0])

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new item
        response = self.post_item(
            name='Bryan\'s kitchen', kind='Kitchen', floor_id=floor_id,
            occupancy={'nb_permanents': 6, 'nb_max': 66},
            spatial_info={'area': 10, 'max_height': 2},
            description='Maybe there is a dog...')
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'Bryan\'s kitchen'
        assert response.json['kind'] == 'Kitchen'
        assert response.json['occupancy']['nb_permanents'] == 6
        assert response.json['occupancy']['nb_max'] == 66
        assert response.json['spatial_info']['area'] == 10
        assert response.json['spatial_info']['max_height'] == 2
        assert response.json['floor_id'] == floor_id

        # Get list: 1 space found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

        # Errors:
        # wrong kind (422)
        response = self.post_item(
            name='wrong_kind_choice', kind='wrong', floor_id=floor_id,
            # occupancy={'nb_permanents': 6, 'nb_max': 66},
            spatial_info={'area': 10, 'max_height': 2})
        assert response.status_code == 422
        # missing kind (201)
        response = self.post_item(
            name='missing_kind', floor_id=floor_id,
            occupancy={'nb_permanents': 6, 'nb_max': 66},
            spatial_info={'area': 10, 'max_height': 2})
        assert response.status_code == 201

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only', kind='Bathroom',
            occupancy={'nb_permanents': 6, 'nb_max': 66},
            spatial_info={'area': 10, 'max_height': 2}, floor_id=floor_id)
        assert response.status_code == 201
        assert response.json['id'] != new_id

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True}], indirect=True)
    def test_views_spaces_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        space_id = str(init_db_data['spaces'][0])

        space_json = self.get_item_by_id(item_id=space_id)
        assert space_json.status_code == 200
        floor_id = str(space_json.json['floor_id'])
        # get etag value
        etag_value = space_json.headers.get('etag', None)

        # Update...
        s_name_updated = 'Spaces or tabs...'
        response = self.put_item(
            item_id=space_id, name=s_name_updated, floor_id=floor_id,
            kind=space_json.json['kind'],
            occupancy=get_dictionary_no_none(space_json.json['occupancy']),
            spatial_info=get_dictionary_no_none(
                space_json.json['spatial_info']),
            description='awful joke',
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == s_name_updated
        assert response.json['kind'] == space_json.json['kind']
        assert response.json['occupancy'] == space_json.json['occupancy']
        assert response.json['spatial_info'] == space_json.json['spatial_info']
        assert response.json['spatial_info']['area'] > 0
        assert response.json['spatial_info']['max_height'] > 0
        assert response.json['floor_id'] == floor_id

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True}], indirect=True)
    def test_views_spaces_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        space_id = str(init_db_data['spaces'][0])

        # get etag value
        response = self.get_item_by_id(item_id=space_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete...
        response = self.delete_item(
            item_id=space_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Resource is really deleted: not found (404)
        response = self.get_item_by_id(item_id=space_id)
        assert response.status_code == 404

    def test_views_spaces_types(self):
        """Test get_list space types api endpoint"""

        # Get space types
        kwargs = {'uri': '{}types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get space types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsSpacesPermissions(TestCoreApiAuthCert):
    """Spaces api views tests, with authentication"""

    base_uri = '/spaces/'

    @pytest.mark.xfail
    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True}], indirect=True)
    def test_views_spaces_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 spaces in DB, but user 'multi-site' is only allowed
        #  to list spaces for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        space_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for space in response.json:
            site_id = dba.get_parent(Space, space['id'])
            assert uacc.verify_scope([site_id])

        allowed_space_id = str(space_data['id'])
        not_allowed_space_id = str(db_data['spaces'][-1])
        allowed_floor_id = str(space_data['floor_id'])
        not_allowed_floor_id = str(db_data['floors'][-1])

        # GET:
        # allowed space (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_space_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed space (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_space_id)
        assert response.status_code == 403

        # POST:
        # user role is allowed to post a new space on allowed site
        response = self.post_item(
            headers=auth_header,
            name='New space', kind='Kitchen', floor_id=allowed_floor_id,
            occupancy={'nb_permanents': 6, 'nb_max': 66},
            spatial_info={'area': 10, 'max_height': 2})
        assert response.status_code == 201
        # not allowed
        response = self.post_item(
            headers=auth_header,
            name='New space 2', kind='Kitchen', floor_id=not_allowed_floor_id,
            occupancy={'nb_permanents': 6, 'nb_max': 66},
            spatial_info={'area': 10, 'max_height': 2})
        assert response.status_code == 403

        # an allowed floor has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_space_id)
        assert response.status_code == 200

        # UPDATE:
        # allowed space (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_space_id,
            name='Updated-name', kind='Cafeteria', floor_id=allowed_floor_id,
            occupancy={'nb_permanents': 6, 'nb_max': 66},
            spatial_info={'area': 10, 'max_height': 2})
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})

        # not allowed space (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_space_id,
            name='Updated-name', kind='Cafeteria',
            floor_id=not_allowed_floor_id,
            occupancy={'nb_permanents': 6, 'nb_max': 66},
            spatial_info={'area': 10, 'max_height': 2})
        assert response.status_code == 403

        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_space_id)
        assert response.status_code == 200

        # DELETE:
        # allowed space (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=allowed_space_id)
        assert response.status_code == 204
        # not allowed space (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_space_id)
        assert response.status_code == 403

        # an allowed space has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
