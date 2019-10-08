"""Tests for API views APISpec documentation responses."""

import marshmallow as ma

from bemserver.api.extensions.rest_api.doc_responses import (
    build_responses)
from bemserver.api.extensions.rest_api.schemas import ErrorSchema

from tests import TestCoreApi


class TestApiExtensionsDocResponses(TestCoreApi):

    def test_extensions_restapi_doc_responses_build(self):

        # when statuses are None or not a list|tuple
        #  200 and 500 statuses are defaults
        for status_codes in [None, 'bad']:
            doc_rsps = build_responses(status_codes)
            assert 200 in doc_rsps
            assert 500 in doc_rsps
            assert 404 not in doc_rsps
            assert doc_rsps == {
                200: {'description': 'successful operation'},
                500: {'description': 'internal server error'},
            }

        # statuses can be a list or a tuple of integers
        for status_codes in [[404, 500], (404, 500,)]:
            doc_rsps = build_responses(status_codes)
            assert 200 not in doc_rsps
            assert 404 in doc_rsps
            assert 500 in doc_rsps
            assert doc_rsps == {
                404: {'description': 'item not found', 'schema': ErrorSchema},
                500: {'description': 'internal server error'},
            }

        # status code can be a string (at least parsable to int)
        doc_rsps = build_responses(['200'])
        assert doc_rsps == {200: {'description': 'successful operation'}}
        # status code can also not be in default responses (a.k.a. _RESPONSES)
        doc_rsps = build_responses([300])
        assert doc_rsps == {300: {'description': ''}}

        doc_rsps = build_responses(['bad'])
        assert doc_rsps == {}

    def test_extensions_restapi_doc_responses_build_schemas(self):

        class DataSchema(ma.Schema):
            data = ma.fields.String()

        doc_rsps = build_responses([200, 204], schemas={200: DataSchema})
        assert 200 in doc_rsps
        assert 'schema' in doc_rsps[200]
        assert doc_rsps[200]['schema'] == DataSchema
        assert 204 in doc_rsps
        assert 'schema' not in doc_rsps[204]
