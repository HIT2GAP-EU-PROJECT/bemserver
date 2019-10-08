"""Tests for api window views"""

import pytest

from bemserver.api.extensions.database import db_accessor as dba
from bemserver.models import Facade

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen, get_dictionary_no_none
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsWindows(TestCoreApi):
    """Window api views tests"""

    base_uri = '/windows/'

    def test_views_windows_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.parametrize('init_db_data', [{
        'gen_floors': True, 'gen_spaces': True, 'gen_facades': True,
        'gen_windows': True}], indirect=True)
    def test_views_windows_get_list_filter(self, init_db_data):
        """Test get_list (with filter) api endpoint"""

        # retrieve database informations
        facade_id = str(init_db_data['facades'][0])

        # Get list: 4 found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get list with a filter: 2 found
        response = self.get_items(covering='Blind')
        assert response.status_code == 200
        assert len(response.json) == 2

        # Get list with a filter: 4 found
        response = self.get_items(facade_id=facade_id)
        assert response.status_code == 200
        assert len(response.json) == 2

        # Get list with wrong filter: 0 found
        response = self.get_items(covering='Dummy')
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.xfail
    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize('init_db_data', [{
        'gen_floors': True, 'gen_spaces': True, 'gen_facades': True,
        'gen_windows': True}], indirect=True)
    def test_views_windows_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get list:
        # sorting by name descending
        response = self.get_items(sort='-name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'window_D'
        assert response.json[1]['name'] == 'window_C'
        assert response.json[2]['name'] == 'window_B'
        assert response.json[3]['name'] == 'window_A'

        # sorting by name ascending
        response = self.get_items(sort='name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'window_A'
        assert response.json[1]['name'] == 'window_B'
        assert response.json[2]['name'] == 'window_C'
        assert response.json[3]['name'] == 'window_D'

    @pytest.mark.parametrize('init_db_data', [{
        'gen_floors': True, 'gen_spaces': True, 'gen_facades': True,
        'gen_windows': True}], indirect=True)
    def test_views_windows_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        window_id = str(init_db_data['windows'][0])

        # Get by its ID
        response = self.get_item_by_id(item_id=window_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=window_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize('init_db_data', [{
        'gen_floors': True, 'gen_spaces': True, 'gen_facades': True
        }], indirect=True)
    def test_views_windows_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        facade_id = str(init_db_data['facades'][0])

        # Get list: none yet
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new item
        response = self.post_item(
            name='Open window', covering='Curtain', facade_id=facade_id,
            surface_info={'area': 2.2}, orientation='South_West', u_value=2.12)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'Open window'
        assert response.json['covering'] == 'Curtain'
        assert response.json['surface_info']['area'] == 2.2
        assert response.json['orientation'] == 'South_West'
        assert response.json['facade_id'] == facade_id
        assert response.json['u_value'] == 2.12

        # Get list: 1 found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

        # Errors:
        # wrong covering (422)
        response = self.post_item(
            name='wrong_cov_choice', covering='wrong', facade_id=facade_id,
            surface_info={'area': 2.2}, orientation='South_West')
        assert response.status_code == 422
        # wrong orientation
        response = self.post_item(
            name='wrong_orientation', covering='Curtain', facade_id=facade_id,
            surface_info={'area': 2.2}, orientation='Nowhere')
        assert response.status_code == 422

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only', covering='Curtain',
            surface_info={'area': 2.2}, orientation='South_West',
            facade_id=facade_id)
        assert response.status_code == 201
        assert response.json['id'] != new_id

    @pytest.mark.parametrize('init_db_data', [{
        'gen_floors': True, 'gen_spaces': True, 'gen_facades': True,
        'gen_windows': True}], indirect=True)
    def test_views_windows_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        window_id = str(init_db_data['windows'][0])

        window_json = self.get_item_by_id(item_id=window_id)
        assert window_json.status_code == 200
        facade_id = str(window_json.json['facade_id'])
        # get etag value
        etag_value = window_json.headers.get('etag', None)

        # Update...
        w_name_updated = 'New window'
        response = self.put_item(
            item_id=window_id, name=w_name_updated, covering='Shade',
            surface_info=get_dictionary_no_none(
                window_json.json['surface_info']),
            facade_id=facade_id, u_value=43421.32,
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == w_name_updated
        assert response.json['covering'] == 'Shade'
        assert (get_dictionary_no_none(response.json['surface_info']) ==
                get_dictionary_no_none(window_json.json['surface_info']))
        assert response.json['facade_id'] == facade_id
        assert response.json['u_value'] == 43421.32

    @pytest.mark.parametrize('init_db_data', [{
        'gen_floors': True, 'gen_spaces': True, 'gen_facades': True,
        'gen_windows': True}], indirect=True)
    def test_views_windows_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        window_id = str(init_db_data['windows'][0])

        # get etag value
        response = self.get_item_by_id(item_id=window_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete...
        response = self.delete_item(
            item_id=window_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Resource is really deleted: not found (404)
        response = self.get_item_by_id(item_id=window_id)
        assert response.status_code == 404

    def test_views_windows_covering_types(self):
        """Test get_list window covering types api endpoint"""

        # Get window covering types
        kwargs = {'uri': '{}covering_types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get window covering types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsWindowsPermissions(TestCoreApiAuthCert):
    """Windows api views tests, with authentication"""

    base_uri = '/windows/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_facades': True,
         'gen_windows': True}
        ], indirect=True)
    def test_views_windows_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 windows in DB, but user 'multi-site' is only allowed
        #  to list windows for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        window_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for window in response.json:
            site_id = dba.get_parent(Facade, window['facade_id'])
            assert uacc.verify_scope(sites=[site_id])

        not_allowed_window_id = str(db_data['windows'][-1])
        allowed_facade_id = str(window_data['facade_id'])
        not_allowed_facade_id = str(db_data['facades'][-1])

        # POST:
        # user role is allowed to post a new window on allowed site
        response = self.post_item(
            headers=auth_header, name='New window', covering='Curtain',
            facade_id=allowed_facade_id, surface_info={'area': 2.2},
            orientation='South_West', u_value=2.12)
        assert response.status_code == 201
        window_data = response.json
        allowed_window_id = str(window_data['id'])
        # not allowed
        response = self.post_item(
            headers=auth_header, name='New window 2', covering='Curtain',
            facade_id=not_allowed_facade_id, surface_info={'area': 2.2},
            orientation='South_West', u_value=2.12)
        assert response.status_code == 403

        # an allowed window has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        # GET:
        # allowed window (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_window_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed window (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_window_id)
        assert response.status_code == 403

        # UPDATE:
        # allowed window (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_window_id,
            name='Updated-name', covering=window_data['covering'],
            orientation=window_data['orientation'],
            surface_info=window_data['surface_info'],
            u_value=window_data['u_value'], facade_id=allowed_facade_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed window (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_window_id,
            name='Updated-name', covering=window_data['covering'],
            orientation=window_data['orientation'],
            surface_info=window_data['surface_info'],
            u_value=window_data['u_value'], facade_id=not_allowed_facade_id)
        assert response.status_code == 403

        # DELETE:
        # allowed slab (in fact parent site)
        response = self.delete_item(headers=headers, item_id=allowed_window_id)
        assert response.status_code == 204
        # not allowed slab (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_window_id)
        assert response.status_code == 403

        # an allowed slab has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
