"""Tests for api occupant views"""

import pytest

from tests import TestCoreApi
from tests.utils import uuid_gen, get_dictionary_no_none


@pytest.mark.usefixtures('init_app')
class TestApiViewsOccupants(TestCoreApi):
    """Occupant api views tests"""

    base_uri = '/occupants/'

    def test_views_occupants_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupants': True}], indirect=True)
    def test_views_occupants_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get list: 4 items found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get list with a filter: age_category found
        response = self.get_items(age_category='ac_65')
        assert response.status_code == 200
        assert len(response.json) == 2

    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupants': True}], indirect=True)
    def test_views_occupants_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get list:
        # sorting by token_id descending
        response = self.get_items(sort='-token_id')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['token_id'] == '789101'
        assert response.json[1]['token_id'] == '151618'
        assert response.json[2]['token_id'] == '123456'
        assert response.json[3]['token_id'] == '121314'

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupants': True}], indirect=True)
    def test_views_occupants_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        occupant_id = str(init_db_data['occupants'][0])

        # Get occupant by its ID
        response = self.get_item_by_id(item_id=occupant_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get occupant by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=occupant_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    def test_views_occupants_post(self):
        """Test post api endpoint"""

        # Post a new occupant
        response = self.post_item(
            token_id='123456', gender='Male',
            age_category='ac_65',
            workspace={'kind': 'office', 'desk_location_window': 'far'})
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['token_id'] == '123456'
        assert response.json['gender'] == 'Male'
        assert response.json['age_category'] == 'ac_65'
        assert response.json['workspace']['kind'] == 'office'
        assert response.json['workspace']['desk_location_window'] == 'far'

        # Errors:
        # AgeCategory not a number (422)
        response = self.post_item(
            token_id='123456', gender='Male', age_category='wrong',
            workspace={'desk_location_window': 'far', 'kind': 'office'})
        assert response.status_code == 422

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupants': True}], indirect=True)
    def test_views_occupants_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        occupant_id = str(init_db_data['occupants'][0])

        occupant_json = self.get_item_by_id(item_id=occupant_id)
        assert occupant_json.status_code == 200
        # get etag value
        etag_value = occupant_json.headers.get('etag', None)

        workspace = get_dictionary_no_none(occupant_json.json['workspace'])

        # Update occupant...
        gender_updated = 'Female'
        response = self.put_item(
            item_id=occupant_id, gender=gender_updated,
            age_category='ac_65',
            workspace=workspace,
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['gender'] == gender_updated
        assert response.json['age_category'] == 'ac_65'
        assert response.json['workspace']['kind'] == 'office'
        assert response.json['workspace']['desk_location_window'] == 'far'

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupants': True}], indirect=True)
    def test_views_occupants_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        occupant_id = str(init_db_data['occupants'][0])

        # get etag value
        response = self.get_item_by_id(item_id=occupant_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a occupant...
        response = self.delete_item(
            item_id=occupant_id, headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Occupant is really deleted: not found (404)
        response = self.get_item_by_id(item_id=occupant_id)
        assert response.status_code == 404

    def test_views_occupants_gender_types(self):
        """Test get_list gender types api endpoint"""

        # Get gender types
        kwargs = {'uri': '{}gender_types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get Gender types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_occupants_age_categories(self):
        """Test get_list age categories api endpoint"""

        # Get age categories
        kwargs = {'uri': '{}age_categories/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_occupants_workspace_types(self):
        """Test get_list workspace types api endpoint"""

        # Get workspace types
        kwargs = {'uri': '{}workspace_types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_occupants_distancetopoint_types(self):
        """Test get_list distancetopoint types api endpoint"""

        # Get distance to point types
        kwargs = {'uri': '{}distancetopoint_types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_occupants_knowledge_levels(self):
        """Test get_list knowledge levels api endpoint"""

        # Get knowledge levels
        kwargs = {'uri': '{}knowledge_levels/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_occupants_activity_frequencies(self):
        """Test get_list activity frequencies api endpoint"""

        # Get activity frequencies
        kwargs = {'uri': '{}activity_frequencies/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    @pytest.mark.skip
    def test_views_occupants_electronic_families_and_types(self):
        """Test get_list electronic families and types api endpoints"""

        # Get electronic families
        kwargs = {'uri': '{}electronic_families/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0
        electronic_families = response.json

        etag_value = response.headers.get('etag', None)
        # Get with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

        # Get electronic types by family
        for cur_family in electronic_families:
            kwargs = {'uri': '{}electronic_families/{}'.format(
                self.base_uri, cur_family['name'])}
            response = self.get_items(**kwargs)
            assert response.status_code == 200
            assert len(response.json) > 0

            etag_value = response.headers.get('etag', None)
            # Get with etag value: not modified (304)
            response = self.get_items(
                headers={'If-None-Match': etag_value}, **kwargs)
            assert response.status_code == 304
