"""Tests for api query extensions"""

import marshmallow as ma

from bemserver.api.extensions.rest_api.query import SortQueryArgsSchema

from tests import TestCoreApi


class TestApiExtensionsQuery(TestCoreApi):
    """Rest api query extensions tests"""

    def test_api_extensions_query_sort_field(self):
        """Test rest api query sort field"""

        class SampleQueryArgsSchema(SortQueryArgsSchema):
            """Sample sort query parameters schema"""
            class Meta:
                strict = True
            name = ma.fields.String()
            number = ma.fields.Integer()

        query_params = SampleQueryArgsSchema().load({
            'name': 'test', 'number': 12,
            'sort': '-name,+number'
            }).data

        assert query_params['sort'] == [('name', -1), ('number', 1)]

        query_params = SampleQueryArgsSchema().load({
            'name': 'test', 'number': 12,
            'sort': 'name,-number'
            }).data

        assert query_params['sort'] == [('name', 1), ('number', -1)]
