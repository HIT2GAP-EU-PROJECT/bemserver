"""Tests for api hateoas extensions"""

import pytest

from tests import TestCoreApi


@pytest.mark.usefixtures('app_mock')
class TestApiExtensionsHateoas(TestCoreApi):
    """Hateoas api extensions tests"""

    base_uri = None

    def test_api_extensions_hateoas_links(self):
        """Test hateoas api endpoint, explore links things..."""

        def _assert_response(resp_data):
            # do we have '_links' attribute ?
            assert '_links' in resp_data
            # and is it as expected ?
            expected_links = {
                'self': '/songs/{}'.format(resp_data['id']),
                'collection': '/songs/',
                'parent': '/albums/{}'.format(resp_data['album_id']),
            }
            assert resp_data['_links'] == expected_links

            # no '_embedded' attribute here
            assert '_embedded' not in resp_data

        # get songs resources
        response = self.get_items(uri='/songs/')
        assert response.status_code == 200
        assert len(response.json) > 0
        _assert_response(response.json[0])

        # get song resource by id
        response = self.get_items(uri='/songs/66')
        assert response.status_code == 200
        _assert_response(response.json)

        # post song resource
        response = self.post_item(
            uri='/songs/', id=666, name='Sardine\'s song!', album_id=123)
        assert response.status_code == 201
        _assert_response(response.json)

    def test_api_extensions_hateoas_embedded(self):
        """Test hateoas api endpoint, explore embedded things..."""

        def _assert_response(resp_data):
            # do we have '_links' attribute ?
            assert '_links' in resp_data
            # and is it as expected ?
            expected_links = {
                'self': '/albums/{}'.format(resp_data['id']),
                'collection': '/albums/',
            }
            assert resp_data['_links'] == expected_links

            # do we have '_embedded' attribute ?
            assert '_embedded' in resp_data
            # and is it as expected ?
            expected_embedded = {
                'songs': {
                    '_links': {
                        'collection': '/songs/?album_id={}'.format(
                            resp_data['id']),
                    },
                }
            }
            assert resp_data['_embedded'] == expected_embedded

        # get albums resources
        response = self.get_items(uri='/albums/')
        assert response.status_code == 200
        assert len(response.json) > 0
        _assert_response(response.json[0])

        # get album resource by id
        response = self.get_items(uri='/albums/99')
        assert response.status_code == 200
        _assert_response(response.json)

        # post album resource
        response = self.post_item(
            uri='/albums/', id=42, name='Punk in Drublic')
        assert response.status_code == 201
        _assert_response(response.json)
