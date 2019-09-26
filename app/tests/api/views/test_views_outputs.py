"""Tests for api output views"""

import pytest

from tests import TestCoreApi
from tests.utils import uuid_gen


@pytest.mark.usefixtures('init_app')
class TestApiViewsEventOutputs(TestCoreApi):
    """Output api views tests"""

    base_uri = '/outputs/events/'

    def test_views_event_outputs_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get output list: no outputs
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_outputs': True}], indirect=True)
    def test_views_event_outputs_get_list_filter(self, init_db_data):
        """Test get_list (with filter) api endpoint"""

        # retrieve database informations
        service_id = str(init_db_data['services'][0])

        # Get output list: 2 outputs found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 2

        etag_value = response.headers.get('etag', None)
        # Get output list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get output list with a filter: 1 found
        response = self.get_items(module_id=service_id)
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_outputs': True}], indirect=True)
    def test_views_event_outputs_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        output_id = str(init_db_data['outputs'][0])
        ts_output_id = str(init_db_data['outputs'][2])

        # Get output by its ID
        response = self.get_item_by_id(item_id=output_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get output by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=output_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404
        response = self.get_item_by_id(item_id=ts_output_id)
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_services': True, 'gen_models': True}],
        indirect=True)
    def test_views_event_outputs_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        service_id = str(init_db_data['services'][0])
        model_id = str(init_db_data['models'][0])

        # Get output list: no outputs
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new output
        response = self.post_item(module_id=service_id, model_id=model_id)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['model_id'] == model_id

        # Get output list: 1 output found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_outputs': True}], indirect=True)
    def test_views_event_outputs_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        output_id = str(init_db_data['outputs'][0])
        model_id = str(init_db_data['models'][1])

        response = self.get_item_by_id(item_id=output_id)
        assert response.status_code == 200
        output = response.json
        etag_value = response.headers.get('etag', None)

        # Update output...
        del output['id']
        output['model_id'] = model_id
        response = self.put_item(
            item_id=output_id, **output, headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['model_id'] == model_id

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_outputs': True}], indirect=True)
    def test_views_event_outputs_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        output_id = str(init_db_data['outputs'][0])

        # get etag value
        response = self.get_item_by_id(item_id=output_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a output...
        response = self.delete_item(
            item_id=output_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Output is really deleted: not found (404)
        response = self.get_item_by_id(item_id=output_id)
        assert response.status_code == 404


@pytest.mark.usefixtures('init_app')
class TestApiViewsTimeSeriesOutputs(TestCoreApi):
    """Output api views tests"""

    base_uri = '/outputs/timeseries/'

    def test_views_timeseries_outputs_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get output list: no outputs
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_outputs': True}], indirect=True)
    def test_views_timeseries_outputs_get_list_filter(self, init_db_data):
        """Test get_list (with filter) api endpoint"""

        # retrieve database informations
        service_id = str(init_db_data['services'][0])

        # Get output list: 2 outputs found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 2

        etag_value = response.headers.get('etag', None)
        # Get output list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get output list with a filter: 1 found
        response = self.get_items(module_id=service_id)
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_outputs': True}], indirect=True)
    def test_views_timeseries_outputs_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        output_id = str(init_db_data['outputs'][2])
        event_output_id = str(init_db_data['outputs'][0])

        # Get output by its ID
        response = self.get_item_by_id(item_id=output_id)
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get output by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=output_id,
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404
        response = self.get_item_by_id(item_id=event_output_id)
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_services': True, 'gen_models': True}],
        indirect=True)
    def test_views_timeseries_outputs_post(self, init_db_data):
        """Test post api endpoint"""

        # retrieve database informations
        site_id = str(init_db_data['sites'][0])
        service_id = str(init_db_data['services'][0])
        model_id = str(init_db_data['models'][0])

        # Get output list: no outputs
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post a new output
        response = self.post_item(
            localization=site_id, module_id=service_id, model_id=model_id,
            values_desc={
                'kind': 'Temperature', 'unit': 'DegreeCelsius', 'sampling': 20
            })
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['model_id'] == model_id

        # Get output list: 1 output found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_outputs': True}], indirect=True)
    def test_views_timeseries_outputs_update(self, init_db_data):
        """Test put api endpoint"""

        # retrieve database informations
        output_id = str(init_db_data['outputs'][2])
        model_id = str(init_db_data['models'][1])

        response = self.get_item_by_id(item_id=output_id)
        assert response.status_code == 200
        output = response.json
        etag_value = response.headers.get('etag', None)

        # Update output...
        del output['id']
        output['model_id'] = model_id
        response = self.put_item(
            item_id=output_id, **output, headers={'If-Match': etag_value})
        # ...update done
        assert response.status_code == 200
        assert response.json['model_id'] == model_id

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_outputs': True}], indirect=True)
    def test_views_timeseries_outputs_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        output_id = str(init_db_data['outputs'][2])

        # get etag value
        response = self.get_item_by_id(item_id=output_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete a output...
        response = self.delete_item(
            item_id=output_id,
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Output is really deleted: not found (404)
        response = self.get_item_by_id(item_id=output_id)
        assert response.status_code == 404
