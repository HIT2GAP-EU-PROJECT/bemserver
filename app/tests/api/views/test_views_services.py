"""Tests for api service views"""

import pytest

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsServices(TestCoreApi):
    """Service api views tests"""

    base_uri = '/services/'

    def test_views_services_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get service list: no services
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_services': True}], indirect=True)
    def test_views_services_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get service list: 4 services found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get service list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get service list with a filter: 1 found
        response = self.get_items(name='service_A')
        assert response.status_code == 200
        assert len(response.json) == 1

        # Get service list: 2 services found
        response = self.get_items(has_frontend=True)
        assert response.status_code == 200
        assert len(response.json) == 2

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_services': True}], indirect=True)
    def test_views_services_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        service_id = str(init_db_data['services'][0])

        # Get service by its ID
        response = self.get_item_by_id(item_id=service_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get service by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=service_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_sites': True}], indirect=True)
    def test_views_services_post(self, init_db_data):
        """Test post api endpoint"""

        # Get service list: no services
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new service
        response = self.post_item(
            name='Service_A', site_ids=[str(init_db_data['sites'][0])],
            has_frontend=False)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'Service_A'
        assert not response.json['has_frontend']

        # Get service list: 1 service found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_services': True}], indirect=True)
    def test_views_services_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        service_id = str(init_db_data['services'][0])

        response = self.get_item_by_id(item_id=service_id)
        assert response.status_code == 200
        service = response.json
        etag_value = response.headers.get('etag', None)

        # Update service...
        del service['id']
        service['name'] = 'Service_C'
        response = self.put_item(
            item_id=service_id, **service, headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == 'Service_C'

        response = self.get_item_by_id(item_id=service_id)
        assert response.status_code == 200
        assert response.json['name'] == 'Service_C'

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_services': True}], indirect=True)
    def test_views_services_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        service_id = str(init_db_data['services'][0])

        # get etag value
        response = self.get_item_by_id(item_id=service_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a service...
        response = self.delete_item(
            item_id=service_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Service is really deleted: not found (404)
        response = self.get_item_by_id(item_id=service_id)
        assert response.status_code == 404

    # TODO: test_views_services_types
#     def test_views_services_types(self):
#         """Test get_list service types api endpoint"""
#
#         # Get service types
#         kwargs = {'uri': '{}types/'.format(self.base_uri)}
#         response = self.get_items(**kwargs)
#         assert response.status_code == 200
#         assert len(response.json) > 0
#
#         etag_value = response.headers.get('etag', None)
#         # Get service types with etag value: not modified (304)
#         response = self.get_items(
#             headers={'If-None-Match': etag_value}, **kwargs)
#         assert response.status_code == 304


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsServicesPermissions(TestCoreApiAuthCert):
    """Sensors api views tests, with authentication"""

    base_uri = '/services/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_services': True}], indirect=True)
    def test_views_services_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 services in DB, but user 'multi-site' is only allowed
        #  to list services for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 2
        service_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for service in response.json:
            assert len(set(uacc.sites).intersection(
                set(str(site_id) for site_id in service['site_ids']))) > 0

        allowed_service_id = str(service_data['id'])
        not_allowed_service_id = str(db_data['services'][-1])

        # GET:
        # allowed service (in fact related site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_service_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed service (in fact related site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_service_id)
        assert response.status_code == 403

        # POST:
        # user role is not allowed at all to post a new service
        #  (even if the site is supposed to be allowed)
        response = self.post_item(
            headers=auth_header,
            name='New service', site_ids=[str(db_data['sites'][0])])
        assert response.status_code == 403

        # no new service has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 2

        # UPDATE:
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        # can not update service (even if related site access is allowed)
        response = self.put_item(
            headers=headers, item_id=allowed_service_id,
            name='Updated-name', site_ids=service_data['site_ids'])
        assert response.status_code == 403

        # DELETE:
        # can not delete service (even if related site access is allowed)
        response = self.delete_item(
            headers=headers, item_id=allowed_service_id)
        assert response.status_code == 403

        # no new service has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 2
