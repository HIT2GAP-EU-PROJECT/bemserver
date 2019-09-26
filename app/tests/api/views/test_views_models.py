"""Tests for api model views"""

import pytest

from tests import TestCoreApi
from tests.utils import uuid_gen


@pytest.mark.usefixtures('init_app')
class TestApiViewsModels(TestCoreApi):
    """Model api views tests"""

    base_uri = '/models/'

    def test_views_models_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get model list: no models
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_models': True}], indirect=True)
    def test_views_models_get_list_filter(self, init_db_data):
        """Test get_list (with filter) api endpoint"""

        # retrieve database informations
        service_id = str(init_db_data['services'][0])

        # Get model list: 2 models found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 2

        etag_value = response.headers.get('etag', None)
        # Get model list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get model list with a filter: 1 found
        response = self.get_items(service_id=service_id)
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_models': True}], indirect=True)
    def test_views_models_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        model_id = str(init_db_data['models'][0])

        # Get model by its ID
        response = self.get_item_by_id(item_id=model_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get model by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=model_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_services': True}], indirect=True)
    def test_views_models_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        service_id = str(init_db_data['services'][0])

        # Get model list: no models
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new model
        response = self.post_item(
            name='Model_A', service_id=service_id,
            parameters=[{'name': 'param', 'value': 12}]
        )
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['name'] == 'Model_A'
        assert response.json['parameters'] == [{'name': 'param', 'value': 12}]

        # Get model list: 1 model found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_models': True}], indirect=True)
    def test_views_models_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        model_id = str(init_db_data['models'][0])

        response = self.get_item_by_id(item_id=model_id)
        assert response.status_code == 200
        model = response.json
        etag_value = response.headers.get('etag', None)

        # Update model...
        del model['id']
        model['name'] = 'Model_C'
        response = self.put_item(
            item_id=model_id, **model, headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['name'] == 'Model_C'

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_models': True}], indirect=True)
    def test_views_models_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        model_id = str(init_db_data['models'][0])

        # get etag value
        response = self.get_item_by_id(item_id=model_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a model...
        response = self.delete_item(
            item_id=model_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Model is really deleted: not found (404)
        response = self.get_item_by_id(item_id=model_id)
        assert response.status_code == 404
