"""Tests for api site views"""

import pytest

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen, get_dictionary_no_none
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsSites(TestCoreApi):
    """Site api views tests"""

    base_uri = '/sites/'

    def test_views_sites_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    def test_views_sites_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get list: 4 items found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get list with a filter: 1 item found
        response = self.get_items(name='site_D')
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.xfail
    @pytest.mark.usefixtures('init_app', 'init_db_data')
    def test_views_sites_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get list:
        # sorting by name descending
        response = self.get_items(sort='-name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'site_D'
        assert response.json[1]['name'] == 'site_C'
        assert response.json[2]['name'] == 'site_B'
        assert response.json[3]['name'] == 'site_A'

        # sorting by name ascending
        response = self.get_items(sort='name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'site_A'
        assert response.json[1]['name'] == 'site_B'
        assert response.json[2]['name'] == 'site_C'
        assert response.json[3]['name'] == 'site_D'

    def test_views_sites_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        site_id = str(init_db_data['sites'][0])

        # Get item by its ID
        response = self.get_item_by_id(item_id=site_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get item by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=site_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    def test_views_sites_post(self):
        """Test post api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new item
        response = self.post_item(
            name='New site', geographic_info={'latitude': 6, 'longitude': 66})
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'New site'
        assert response.json['geographic_info']['latitude'] == 6
        assert response.json['geographic_info']['longitude'] == 66
        assert 'description' not in response.json

        # Get list: 1 item found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

        # Errors:
        # missing name (422)
        response = self.post_item(
            geographic_info={'latitude': 6, 'longitude': 66})
        assert response.status_code == 422
        # missing geographical data (422)
        response = self.post_item(name='missing_geo_data')
        assert response.status_code == 422
        # wrong geographical data (422)
        response = self.post_item(name='test_error', geographic_info='wrong')
        assert response.status_code == 422

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only',
            geographic_info={'latitude': 6, 'longitude': 66})
        assert response.status_code == 201
        assert response.json['id'] != new_id

    def test_views_sites_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        site_id = str(init_db_data['sites'][0])
        geo_json = self.get_item_by_id(item_id=site_id).json['geographic_info']
        geo_json_none = get_dictionary_no_none(geo_json)

        # get etag value
        response = self.get_item_by_id(item_id=site_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Update item...
        s_name_updated = 'Updated site'
        response = self.put_item(
            item_id=site_id, name=s_name_updated,
            geographic_info=geo_json_none,
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == s_name_updated
        assert response.json['geographic_info'] == geo_json

    def test_views_sites_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        site_id = str(init_db_data['sites'][0])

        # get etag value
        response = self.get_item_by_id(item_id=site_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete an item...
        response = self.delete_item(
            item_id=site_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Site is really deleted: not found (404)
        response = self.get_item_by_id(item_id=site_id)
        assert response.status_code == 404


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsSitesPermissions(TestCoreApiAuthCert):
    """Sites api views tests, with authentication"""

    base_uri = '/sites/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    def test_views_sites_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET site list:
        # 4 sites in DB, but user 'multi-site' is only allowed to list 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 2
        site_data = response.json[0]
        # verify allowed site IDs and list site IDs are the same
        assert uacc.verify_scope(sites=[site['id'] for site in response.json])

        allowed_site_id = str(site_data['id'])
        not_allowed_site_id = str(db_data['sites'][-1])

        # GET a site:
        # allowed site
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_site_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed site
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_site_id)
        assert response.status_code == 403

        # POST a site:
        # user role is allowed to post a new site
        response = self.post_item(
            headers=auth_header,
            name='New site', geographic_info={'latitude': 6, 'longitude': 66})
        assert response.status_code == 201

        # UPDATE a site:
        # allowed site
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_site_id,
            name='Updated-name', geographic_info=site_data['geographic_info'])
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed site
        response = self.put_item(
            headers=headers, item_id=not_allowed_site_id,
            name='Updated-name', geographic_info=site_data['geographic_info'])
        assert response.status_code == 403

        # DELETE a site:
        # allowed site
        response = self.delete_item(headers=headers, item_id=allowed_site_id)
        assert response.status_code == 204
        # not allowed site
        response = self.delete_item(
            headers=headers, item_id=not_allowed_site_id)
        assert response.status_code == 403

        # an allowed site has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 1
