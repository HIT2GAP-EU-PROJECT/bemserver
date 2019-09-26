"""Tests for api custom fields extensions"""

import pytest
import marshmallow as ma
from werkzeug.datastructures import FileStorage

from bemserver.api.extensions.rest_api.custom_fields import FileField

from tests import TestCoreApi


class TestApiExtensionsCustomFields(TestCoreApi):
    """Rest api custom fields extensions tests"""

    def test_api_extensions_custom_fields_file(self):
        """Test rest api custom file field"""

        class SampleSchema(ma.Schema):
            """Sample custom file field schema"""
            class Meta:
                strict = True
            input_file = FileField(
                allowed_file_extensions=('.pdf',)
            )

        file_storage = FileStorage(filename='test.pdf')

        file_datas = SampleSchema().load({
            'input_file': file_storage
        }).data
        assert file_datas['input_file'] == file_storage

        # Errors
        # validation: wrong file extension
        with pytest.raises(ma.ValidationError):
            SampleSchema().load({
                'input_file': FileStorage(filename='not_valid.zip')
            })
        # validation: wrong value type
        with pytest.raises(ma.ValidationError):
            SampleSchema().load({
                'input_file': 'wrong_type'
            })
