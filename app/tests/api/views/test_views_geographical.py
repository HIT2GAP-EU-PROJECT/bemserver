"""Tests for api geographical information views."""

import pytest

from tests import TestCoreApi


@pytest.mark.usefixtures('init_app')
class TestApiViewsGeographical(TestCoreApi):
    """Tests on geographical api views."""

    base_uri = '/geographical/'

    def test_views_geographical_orientations(self):
        """Test enum orientation types."""

        # Get geographical orientation types
        kwargs = {'uri': '{}orientations/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get geographical orientations with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_geographical_hemispheres(self):
        """Test enum hemisphere types."""

        # Get geographical hemisphere types
        kwargs = {'uri': '{}hemispheres/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get geographical hemisphere types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304

    def test_views_geographical_climates(self):
        """Test enum climate types."""

        # Get geographical climate types
        kwargs = {'uri': '{}climates/'.format(self.base_uri)}
        response = self.get_items(**kwargs)
        assert response.status_code == 200
        assert len(response.json) > 0

        etag_value = response.headers.get('etag', None)
        # Get geographical climate types with etag value: not modified (304)
        response = self.get_items(
            headers={'If-None-Match': etag_value}, **kwargs)
        assert response.status_code == 304
