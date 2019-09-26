"""Tests for api building views"""

import pytest

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.utils import uuid_gen
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


@pytest.mark.usefixtures('init_app')
class TestApiViewsBuildings(TestCoreApi):
    """Building api views tests"""

    base_uri = '/buildings/'

    def test_views_buildings_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get building list: no buildings
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_db_data',
        [{'gen_sites': True, 'gen_buildings': True}],
        indirect=True)
    def test_views_buildings_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get building list: 4 buildings found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get building list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get building list with a filter: 1 found
        response = self.get_items(kind='House')
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.xfail
    @pytest.mark.usefixtures('init_app', 'init_db_data')
    def test_views_buildings_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get building list:
        # sorting by area descending
        response = self.get_items(sort='-area')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'building_D'
        assert response.json[1]['name'] == 'building_B'
        assert response.json[2]['name'] == 'building_A'
        assert response.json[3]['name'] == 'building_C'

        # sorting by area ascending
        response = self.get_items(sort='area')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'building_C'
        assert response.json[1]['name'] == 'building_A'
        assert response.json[2]['name'] == 'building_B'
        assert response.json[3]['name'] == 'building_D'

        # sorting by name descending, area ascending
        response = self.get_items(sort='-name,+area')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['name'] == 'building_D'
        assert response.json[1]['name'] == 'building_C'
        assert response.json[2]['name'] == 'building_B'
        assert response.json[3]['name'] == 'building_A'

    def test_views_buildings_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        building_id = str(init_db_data['buildings'][0])

        # Get building by its ID
        response = self.get_item_by_id(item_id=building_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get building by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=building_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_buildings': False}], indirect=True)
    def test_views_buildings_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        site_id = str(init_db_data['sites'][0])

        # Get building list: no buildings
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new building
        response = self.post_item(
            name='Cartman\'s house', area=9999, kind='House', site_id=site_id)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'Cartman\'s house'
        assert response.json['area'] == 9999
        assert response.json['kind'] == 'House'
        assert response.json['site_id'] == site_id

        # Get building list: 1 building found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

        # Errors:
        # area not a number (422)
        response = self.post_item(
            name='area_not_a_number', area='not_a_number', kind='Cinema',
            site_id=str(uuid_gen()))
        assert response.status_code == 422
        # missing area (422)
        response = self.post_item(name='missing_area', site_id=str(uuid_gen()))
        assert response.status_code == 422

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        response = self.post_item(
            id=new_id, name='id_is_read_only', area=0, kind='Cinema',
            site_id=site_id)  # site_id=str(uuid_gen()))
        assert response.status_code == 201
        assert response.json['id'] != new_id

        # Post new item with non-existing site id -> 422, ref not found
        response = self.post_item(
            name='test', area=69, kind='Cinema',
            site_id=str(uuid_gen()))
        assert response.status_code == 422
        assert response.json['errors'] == {'site_id': ['Reference not found']}

    @pytest.mark.xfail(
        reason='Two issues: '
        '1. When area is set to 0, the data model stores -1. '
        '2. When changing the kind, a new relation is created and the API '
        'returns two buildings.'
    )
    def test_views_buildings_update(self, init_db_data):
        """Test put api endpoint"""

        response = self.get_items()
        assert response.status_code == 200
        initial_nb_of_buildings = len(response.json)

        # retrieve database informations
        building_id = str(init_db_data['buildings'][0])

        response = self.get_item_by_id(item_id=building_id)
        assert response.status_code == 200
        building = response.json

        # get etag value
        etag_value = response.headers.get('etag', None)

        # Update building...
        building_update = building.copy()
        building_update['area'] = 1
        building_update['kind'] = 'OfficeBuilding'
        item_id = building_update.pop('id')
        response = self.put_item(
            item_id=item_id, headers={'If-Match': etag_value},
            **building_update)
        # ...update done
        assert response.status_code == 200

        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == initial_nb_of_buildings

        response = self.get_item_by_id(item_id=building_id)
        assert response.status_code == 200
        updated_building = response.json
        del updated_building['id']
        assert updated_building == building_update

    def test_views_buildings_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        building_id = str(init_db_data['buildings'][0])

        # get etag value
        response = self.get_item_by_id(item_id=building_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a building...
        response = self.delete_item(
            item_id=building_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Building is really deleted: not found (404)
        response = self.get_item_by_id(item_id=building_id)
        assert response.status_code == 404

    def test_views_buildings_types(self):
        """Test get_list building types api endpoint"""

        # Get building types
        kwargs = {'uri': '{}types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get building types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304


@pytest.mark.usefixtures('init_app', 'init_db_data')
class TestApiViewsBuildingsPermissions(TestCoreApiAuthCert):
    """Buildings api views tests, with authentication"""

    base_uri = '/buildings/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize(
        'certificate_data', ['multi-site'], indirect=True)
    def test_views_buildings_permissions(self, certificate_data, init_db_data):
        db_data = init_db_data
        # sign in user
        auth_header = self._auth_cert_login(certificate_data)
        # get authenticated user account
        uacc = self._get_uacc(db_data, 'multi-site')
        assert uacc is not None

        # GET list:
        # 4 builings in DB, but user 'multi-site' is only allowed
        #  to list for 2 sites
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
        building_data = response.json[0]
        # verify that parent site IDs are in allowed site IDs
        assert uacc.verify_scope(sites=[
            building['site_id'] for building in response.json])

        allowed_building_id = str(building_data['id'])
        not_allowed_building_id = str(db_data['buildings'][-1])
        allowed_site_id = str(building_data['site_id'])
        not_allowed_site_id = str(db_data['sites'][-1])

        # GET:
        # allowed building (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=allowed_building_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        # not allowed building (in fact parent site)
        response = self.get_item_by_id(
            headers=auth_header, item_id=not_allowed_building_id)
        assert response.status_code == 403

        # POST:
        # user role is allowed to post a new building on allowed site
        response = self.post_item(
            headers=auth_header,
            name='New building', area=9999, kind='House',
            site_id=allowed_site_id)
        assert response.status_code == 201
        # not allowed
        response = self.post_item(
            headers=auth_header,
            name='New building 2', area=9999, kind='House',
            site_id=not_allowed_site_id)
        assert response.status_code == 403

        # an allowed building has been created...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 4

        # UPDATE:
        # allowed building (in fact parent site)
        headers = auth_header.copy()
        headers.update({'If-Match': etag_value})
        response = self.put_item(
            headers=headers, item_id=allowed_building_id,
            name='Updated-name', area=9999, kind='House',
            site_id=allowed_site_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)
        headers.update({'If-Match': etag_value})
        # not allowed building (in fact parent site)
        response = self.put_item(
            headers=headers, item_id=not_allowed_building_id,
            name='Updated-name', area=9999, kind='House',
            site_id=not_allowed_site_id)
        assert response.status_code == 403

        # DELETE:
        # allowed building (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=allowed_building_id)
        assert response.status_code == 204
        # not allowed building (in fact parent site)
        response = self.delete_item(
            headers=headers, item_id=not_allowed_building_id)
        assert response.status_code == 403

        # an allowed building has been deleted...
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 3
