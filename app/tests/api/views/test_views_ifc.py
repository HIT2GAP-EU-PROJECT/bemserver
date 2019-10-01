"""Tests for api building views"""

from werkzeug.utils import secure_filename
import pytest

from bemserver.api.views.ifc.exceptions import IFCFileBadArchiveError

from tests import TestCoreApi
from tests.utils import uuid_gen
from tests.api.utils import build_file_obj


@pytest.mark.usefixtures('init_app')
class TestApiViewsIFC(TestCoreApi):
    """IFC api views tests"""

    base_uri = '/ifc/'
    subitems_uri = {
        'download': {
            'uri': '/'
        },
        'import': {
            'uri': '/import'
        },
    }

    def test_views_ifc_get_list_empty(self):
        """Test get_list api endpoint"""

        # Get IFC files list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': False, 'gen_ifc_files': True}], indirect=True)
    def test_views_ifc_get_list_filter(self):
        """Test get_list (with filter) api endpoint"""

        # Get item list: 4 items found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 4

        etag_value = response.headers.get('etag', None)
        # Get item list with etag: not modified (304)
        response = self.get_items(headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Get item list with a filter: 1 item found
        response = self.get_items(original_file_name='file_A.ifc')
        assert response.status_code == 200
        assert len(response.json) == 1

    @pytest.mark.usefixtures('init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': False, 'gen_ifc_files': True}], indirect=True)
    def test_views_ifc_get_list_sort(self):
        """Test get_list (with sort) api endpoint"""

        # Get item list:
        # sorting by name descending
        response = self.get_items(sort='-file_name')
        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json[0]['file_name'] == 'file_D.ifc'
        assert response.json[1]['file_name'] == 'file_C.ifc'
        assert response.json[2]['file_name'] == 'file_B.ifc'
        assert response.json[3]['file_name'] == 'file_A.ifc'

    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': False, 'gen_ifc_files': True}], indirect=True)
    def test_views_ifc_get_by_id(self, init_db_data):
        """Test get_by_id api endpoint"""

        # retrieve database informations
        ifc_file_id = next(iter(init_db_data['ifc_files']))

        # Get item by its ID
        response = self.get_item_by_id(item_id=str(ifc_file_id))
        assert response.status_code == 200

        etag_value = response.headers.get('etag', None)
        # Get item by its ID with etag: not modified (304)
        response = self.get_item_by_id(
            item_id=str(ifc_file_id),
            headers={'If-None-Match': etag_value})
        assert response.status_code == 304

        # Errors:
        # not found (404)
        response = self.get_item_by_id(item_id=str(uuid_gen()))
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'ifc_zip_file_obj', ['.zip', '.ifczip'], indirect=True)
    def test_views_ifc_post(
            self, ifc_file_obj, ifc_zip_file_obj, ifc_multi_zip_file_obj):
        """Test post api endpoint"""

        # retrieve ifc file informations
        file_name = ifc_file_obj[0]
        zip_file_name, zip_file_obj = ifc_zip_file_obj
        zip_multi_file_obj = ifc_multi_zip_file_obj[1]

        # Get ifc file list: no items
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 0

        # Post an ifc file
        response = self.post_item(
            description='A description of the file...', file=ifc_file_obj[2],
            content_type='multipart/form-data')
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['original_file_name'] == file_name
        assert response.json['file_name'] == secure_filename(file_name)

        # Get ifc file list: 1 item found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

        # Post a zipped ifc file
        response = self.post_item(
            description='Another description of the file...',
            file=zip_file_obj, content_type='multipart/form-data')
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['original_file_name'] == zip_file_name
        assert response.json['file_name'] == secure_filename(
            zip_file_name)

        # Errors:
        # missing file (422)
        response = self.post_item(content_type='multipart/form-data')
        assert response.status_code == 422
        # wrong file format (422)
        response = self.post_item(
            file=build_file_obj('wrong_format.pdf', 'just a test'),
            content_type='multipart/form-data')
        assert response.status_code == 422
        # wrong file object (422)
        response = self.post_item(
            file='wrong_object.ifc', content_type='multipart/form-data')
        assert response.status_code == 422
        # more than ONE file in zipped archive (500)
        with pytest.raises(IFCFileBadArchiveError):
            self.post_item(
                file=zip_multi_file_obj, content_type='multipart/form-data')

        # Remarks:
        # id is 'read only'
        new_id = str(uuid_gen())
        ifc_file_name = 'id_is_read_only.ifc'
        response = self.post_item(
            id=new_id, file=build_file_obj(ifc_file_name, 'test'),
            content_type='multipart/form-data')
        assert response.status_code == 201
        assert response.json['id'] != new_id

    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': False, 'gen_ifc_files': True}], indirect=True)
    def test_views_ifc_delete(self, init_db_data):
        """Test delete api endpoint"""

        # retrieve database informations
        ifc_file_id = next(iter(init_db_data['ifc_files']))

        # get etag value
        response = self.get_item_by_id(item_id=str(ifc_file_id))
        assert response.status_code == 200
        etag_value = response.headers.get('etag', None)

        # Delete an item...
        response = self.delete_item(
            item_id=str(ifc_file_id),
            headers={'If-Match': etag_value})
        # ...delete done
        assert response.status_code == 204

        # Item is really deleted: not found (404)
        response = self.get_item_by_id(item_id=str(ifc_file_id))
        assert response.status_code == 404

    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': False, 'gen_ifc_files': True}], indirect=True)
    def test_views_ifc_download(self, init_db_data, ifc_file_obj):
        """Test download api endpoint"""

        # retrieve database informations
        ifc_file_id = next(iter(init_db_data['ifc_files']))

        # retrieve ifc file informations
        file_content = ifc_file_obj[1]

        # Download file
        response = self.get_subitem_by_id(
            item_id=str(ifc_file_id),
            subitem_params={'download': {
                'item_id': init_db_data['ifc_files'][ifc_file_id]}})
        assert response.status_code == 200
        assert response.data == bytes(file_content, 'utf-8')

        # Errors:
        # file id not found (404)
        response = self.get_subitem_by_id(
            item_id=str(uuid_gen()),
            subitem_params={'download': {'item_id': 'not_found'}})
        assert response.status_code == 404
        # file name not corresponding: not found (404)
        response = self.get_subitem_by_id(
            item_id=str(ifc_file_id),
            subitem_params={'download': {'item_id': 'not_expected_file_name'}})
        assert response.status_code == 404

    @pytest.mark.parametrize('init_db_data', [
        {'gen_buildings': False, 'gen_ifc_files': True}], indirect=True)
    def test_views_ifc_import(self, init_db_data):
        """Test import api endpoint"""

        # retrieve database informations
        ifc_file_id = next(iter(init_db_data['ifc_files']))

        # Import file
        response = self.post_subitem(
            item_id=str(ifc_file_id), subitem_params={'import': None})
        assert response.status_code == 201
        assert response.json['success']

        # Errors:
        # file id not found (404)
        response = self.post_subitem(
            item_id=str(uuid_gen()), subitem_params={'import': None})
        assert response.status_code == 404
