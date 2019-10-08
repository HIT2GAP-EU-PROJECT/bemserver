"""Tests for api comfort views"""

import datetime as dt

import pytest
from tests import TestCoreApi
from tests.utils import uuid_gen


@pytest.mark.usefixtures('init_app')
class TestApiViewsComforts(TestCoreApi):
    """Comfort api views tests"""

    base_uri = '/comforts/'

    def test_views_comforts_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize('init_db_data', [{
        'gen_occupants': True, 'gen_comforts': True}], indirect=True)
    def test_views_comforts_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get list: 4 items found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize('init_db_data', [{
        'gen_occupants': True, 'gen_comforts': True}], indirect=True)
    def test_views_comforts_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get comfort list:
        # sorting by name descending
        response = self.get_items(sort='-time')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['description'] == 'comfort version D'
        assert response.json[1]['description'] == 'comfort version C'
        assert response.json[2]['description'] == 'comfort version B'
        assert response.json[3]['description'] == 'comfort version A'

        # sorting by name ascending
        response = self.get_items(sort='time')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['description'] == 'comfort version A'
        assert response.json[1]['description'] == 'comfort version B'
        assert response.json[2]['description'] == 'comfort version C'
        assert response.json[3]['description'] == 'comfort version D'

    @pytest.mark.parametrize('init_db_data', [{
        'gen_occupants': True, 'gen_comforts': True}], indirect=True)
    def test_views_comforts_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        comfort_id = str(init_db_data['comforts'][0])

        # Get comfort by its ID
        response = self.get_item_by_id(item_id=comfort_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get comfort by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=comfort_id, headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupants': True}], indirect=True)
    def test_views_comforts_post(self, init_db_data):
        """Test post api endpoint"""

        occupant_id = str(init_db_data['occupants'][0])

        # Post a new comfort
        response = self.post_item(
            occupant_id=occupant_id,
            time=dt.datetime(2017, 4, 11, 8, 34, 7).isoformat(),
            perceptions=[{
                'aspect_type': 'air_humidity',
                'perception': 3,
                'satisfaction': 2,
                'preference': 'lower'}])
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['time'] == '2017-04-11T08:34:07+00:00'
        assert len(response.json['perceptions']) == 1

        # Errors:
        # not valide comfort type  (422)
        response = self.post_item(
            occupant_id=occupant_id,
            time=dt.datetime(2017, 4, 11, 8, 34, 7).isoformat(),
            description='comfort du 8 juin',
            perceptions=[{
                'aspect_type': 'wrong',
                'perception': 3,
                'satisfaction': 2,
                'preference': 'lower'}])
        assert response.status_code == 422

    @pytest.mark.parametrize('init_db_data', [{
        'gen_occupants': True, 'gen_comforts': True}], indirect=True)
    def test_views_comforts_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        comfort_id = str(init_db_data['comforts'][0])

        # get etag value
        comfort_json = self.get_item_by_id(item_id=comfort_id)
        assert comfort_json.status_code == 200
        etag_value = comfort_json.headers.get('etag', None)

        # Update comfort...
        s_tim = '2017-06-11T08:34:07+00:00'
        response = self.put_item(
            item_id=comfort_id,
            occupant_id=str(comfort_json.json['occupant_id']), time=s_tim,
            headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['id'] is not None
        assert response.json['time'] == s_tim
        assert response.json['perceptions'] == []

    @pytest.mark.parametrize('init_db_data', [{
        'gen_occupants': True, 'gen_comforts': True}], indirect=True)
    def test_views_comforts_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        comfort_id = str(init_db_data['comforts'][0])

        # get etag value
        response = self.get_item_by_id(item_id=comfort_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a comfort...
        response = self.delete_item(
            item_id=comfort_id, headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Comfort is really deleted: not found (404)
        response = self.get_item_by_id(item_id=comfort_id)
        assert response.status_code == 404

    def test_views_comforts_preference_types(self):
        """Test get_list preference types api endpoint"""

        # Get preference types
        kwargs = {'uri': '{}preference_types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_comforts_comfort_types(self):
        """Test get_list comfort aspects types api endpoint"""

        # Get preference types
        kwargs = {'uri': '{}comfort_types/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304
