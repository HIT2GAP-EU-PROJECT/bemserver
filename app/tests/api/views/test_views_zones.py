"""Tests for api zone views"""

import pytest

from bemserver.api.extensions.database import db_accessor as dba
from bemserver.models import Building

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsZones(TestCoreApi):
    """Zone api views tests"""

    base_uri = '/zones/'

    def test_views_zones_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_zones': True}
        ], indirect=True)
    def test_views_zones_get_list_filter(self, init_db_data):
        """Test get_list (with filter) api endpoint"""

        # retrieve database informations
        building_id = str(init_db_data['buildings'][0])

        # Get list: 4 found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get list with a filter: 4 zones found
        response = self.get_items(building_id=building_id)
        assert response.status_code == 200
        assert len(response.json) == 2

    @pytest.mark.xfail
    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_zones': True}
        ], indirect=True)
    def test_views_zones_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get list:
        # sorting by name descending
        response = self.get_items(sort='-name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'zone_D'
        assert response.json[1]['name'] == 'zone_C'
        assert response.json[2]['name'] == 'zone_B'
        assert response.json[3]['name'] == 'zone_A'

        # sorting by name ascending
        response = self.get_items(sort='name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'zone_A'
        assert response.json[1]['name'] == 'zone_B'
        assert response.json[2]['name'] == 'zone_C'
        assert response.json[3]['name'] == 'zone_D'

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_zones': True}
        ], indirect=True)
    def test_views_zones_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        zone_id = str(init_db_data['zones'][0])

        # Get by its ID
        response = self.get_item_by_id(item_id=zone_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=zone_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': True, 'gen_floors': True, 'gen_spaces': True}
        ], indirect=True)
    def test_views_zones_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        building_id = str(init_db_data['buildings'][0])

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post new item with non-existing space id -> 422, ref not found
        z_spaces = [str(uuid_gen())]
        response = self.post_item(
            name='Zone 51', spaces=z_spaces, building_id=building_id)
        assert response.status_code == 422
        assert response.json['errors'] == {
            'spaces': {'0': ['Reference not found']}}

        # Post a new item - with an existing space ID
        z_spaces = [str(init_db_data['spaces'][0])]
        response = self.post_item(
            name='Zone 51', spaces=z_spaces, building_id=building_id)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'Zone 51'
        assert response.json['zones'] == []
        assert response.json['spaces'] == z_spaces
        assert 'description' not in response.json

        # Get list: 1 found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only', spaces=z_spaces,
            building_id=building_id)
        assert response.status_code == 201
        assert response.json['id'] != new_id

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_zones': True}
        ], indirect=True)
    def test_views_zones_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        zone_id = str(init_db_data['zones'][0])

        zone_json = self.get_item_by_id(item_id=zone_id)
        assert zone_json.status_code == 200

        # get etag value
        building_id = str(zone_json.json['building_id'])
        etag_value = zone_json.headers.get('etag', None)

        # Update...
        z_name_updated = 'Trap zone'
        response = self.put_item(
            item_id=zone_id, name=z_name_updated,
            zones=zone_json.json['zones'], spaces=zone_json.json['spaces'],
            building_id=building_id, headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == z_name_updated
        assert set(response.json['zones']) == set(zone_json.json['zones'])
        assert set(response.json['spaces']) == set(zone_json.json['spaces'])

    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_zones': True}
        ], indirect=True)
    def test_views_zones_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        zone_id = str(init_db_data['zones'][0])

        # get etag value
        response = self.get_item_by_id(item_id=zone_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete...
        response = self.delete_item(
            item_id=zone_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Resource is really deleted: not found (404)
        response = self.get_item_by_id(item_id=zone_id)
        assert response.status_code == 404


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsZonesPermissions(TestCoreApiAuthCert):
    """Zones api views tests, with authentication"""

    base_uri = '/zones/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_floors': True, 'gen_spaces': True, 'gen_zones': True}
        ], indirect=True)
    def test_views_zones_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 zones in DB, but user 'multi-site' is only allowed
        #  to list zones for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        zone_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        for zone in response.json:
            site_id = dba.get_parent(Building, zone['building_id'])
            assert uacc.verify_scope(sites=[site_id])

        allowed_zone_id = str(zone_data['id'])
        not_allowed_zone_id = str(db_data['zones'][-1])
        allowed_building_id = str(zone_data['building_id'])
        not_allowed_building_id = str(db_data['buildings'][-1])

        # GET:
        # allowed zone (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_zone_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed zone (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_zone_id)
        assert response.status_code == 403

        # POST:
        # user role is allowed to post a new zone on allowed site
        response = self.post_item(
            headers=auth_header,
            name='New zone', zones=[], spaces=[],
            building_id=allowed_building_id)
        assert response.status_code == 201
        # not allowed
        response = self.post_item(
            headers=auth_header,
            name='New zone 2', zones=[], spaces=[],
            building_id=not_allowed_building_id)
        assert response.status_code == 403

        # an allowed zone has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        # UPDATE:
        # allowed zone (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_zone_id,
            name='Updated-name', zones=[], sapces=zone_data['spaces'],
            building_id=allowed_building_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed zone (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_zone_id,
            name='Updated-name', zones=[], sapces=zone_data['spaces'],
            building_id=not_allowed_building_id)
        assert response.status_code == 403

        # DELETE:
        # allowed zone (in fact parent site)
        response = self.delete_item(headers=headers, item_id=allowed_zone_id)
        assert response.status_code == 204
        # not allowed zone (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_zone_id)
        assert response.status_code == 403

        # an allowed zone has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
