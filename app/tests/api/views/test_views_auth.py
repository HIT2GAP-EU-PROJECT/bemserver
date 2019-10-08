"""Tests for api auth views"""

import pytest

from bemserver.api.extensions.auth import is_auth_enabled

from tests import TestCoreApi
from tests.api.views.conftest import TestingConfig


class TestingConfigAuthEnabled(TestingConfig):
    """App config to test authentication stuff"""
    AUTHENTICATION_ENABLED = True


class TestingConfigAuthJWTEnabled(TestingConfigAuthEnabled):
    """App config to test JWT authentication stuff"""
    AUTH_JWT_ENABLED = True


@pytest.mark.usefixtures('init_app')
class TestApiViewsAuth(TestCoreApi):

    base_uri = '/auth/'

    def _get_protected_resources(self, cookie_data=None):
        headers = None
        if cookie_data is not None:
            headers = {'cookie': cookie_data}
        uri = '/timeseries/Test_1'
        kwargs = {
            'start_time': '2018-01-01T00:00:00Z',
            'end_time': '2018-02-01T00:00:00Z',
        }
        return self.get_items(uri=uri, headers=headers, **kwargs)

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_auth_disabled(self):
        with self.app.app_context():
            assert not is_auth_enabled()

        # /auth/modes endpoint not loaded
        response = self.get_items(extra_uri='modes')
        assert response.status_code == 404

        # Get some protected datas
        response = self._get_protected_resources()
        assert response.status_code == 200

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthEnabled], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_auth_enabled_no_modes(self):
        assert not is_auth_enabled()
        with self.app.app_context():
            assert not is_auth_enabled()

        # no authentication mode enabled
        response = self.get_items(extra_uri='modes')
        assert response.status_code == 200
        assert response.json['auth_modes'] == []

        # Get some protected datas (no need to be logged in)
        response = self._get_protected_resources()
        assert response.status_code == 200

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthJWTEnabled], indirect=True)
    def test_views_auth_modes(self):
        assert not is_auth_enabled()
        with self.app.app_context():
            assert is_auth_enabled()

        # JWT authentication mode enabled
        response = self.get_items(extra_uri='modes')
        assert response.status_code == 200
        assert response.json['auth_modes'] == ['JWT']
