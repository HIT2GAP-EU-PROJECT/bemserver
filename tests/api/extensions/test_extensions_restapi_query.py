"""Tests for api query extensions"""

import pytest
from tests import TestCoreApi

import marshmallow as ma

from h2g_platform_core.api.extensions.rest_api.query import SortQueryArgsSchema


class TestApiExtensionsQuery(TestCoreApi):
    """Rest api query extensions tests"""

    def test_api_extensions_query_sort_field(self):
        # pylint: disable=no-self-use, invalid-name
        """Test rest api query sort field"""

        class SampleQueryArgsSchema(SortQueryArgsSchema):
            # pylint: disable=too-few-public-methods
            """Sample sort query parameters schema"""

            class Meta:  # pylint: disable=missing-docstring
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
