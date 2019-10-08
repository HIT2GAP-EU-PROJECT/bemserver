"""Tests for api auth views"""

import pytest

from bemserver.api.extensions.auth import is_auth_enabled

from tests import TestCoreApi
from tests.api.views.conftest import TestingConfig


class TestingConfigAuthDemoEnabled(TestingConfig):
    """App config to test authentication DEMO stuff"""
    AUTHENTICATION_DEMO_ENABLED = True


class TestingConfigAuthDemoModesEnabled(TestingConfigAuthDemoEnabled):
    """App config to test authentication modes DEMO stuff"""
    AUTH_JWT_ENABLED = True
    AUTH_CERTIFICATE_ENABLED = True


@pytest.mark.usefixtures('init_app')
class TestApiViewsAuthDemo(TestCoreApi):

    base_uri = '/auth/'

    def _get_private_content(
            self, *, case_num=None, access_token=None, cookie_data=None):
        headers = None
        if access_token is not None:
            headers = {'Authorization': 'Bearer {}'.format(access_token)}
        if cookie_data is not None:
            headers = {'cookie': cookie_data}
        extra_uri = 'demo/private'
        if case_num is not None:
            extra_uri = 'demo/private/roles/{}'.format(case_num)
        return self.get_items(extra_uri=extra_uri, headers=headers)

    def _extract_cookie_session(self, set_cookie):
        for set_cookie_part in set_cookie.split(';'):
            if '{}='.format(self.app.session_cookie_name) in set_cookie_part:
                return set_cookie_part.strip()
        return None

    def test_views_auth_demo_disabled(self):
        assert not is_auth_enabled()
        with self.app.app_context():
            assert not is_auth_enabled()

        # authentication is disabled, demo too
        # /auth/modes endpoint not loaded
        response = self.get_items(extra_uri='modes')
        assert response.status_code == 404

        # /auth/demo/private endpoint not loaded
        response = self._get_private_content()
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthDemoEnabled], indirect=True)
    def test_views_auth_demo_enabled(self):
        assert not is_auth_enabled()
        with self.app.app_context():
            assert not is_auth_enabled()

        # authentication (demo) is enabled
        # no authentication mode enabled
        response = self.get_items(extra_uri='modes')
        assert response.status_code == 200
        assert response.json['auth_modes'] == []

        # Get private content (no need to be logged in)
        response = self._get_private_content()
        assert response.status_code == 200
        assert response.json == 'Hello anonymous, access authorized!'

        # Get private content with roles required (no need to be logged in)
        response = self._get_private_content(case_num=0)
        assert response.status_code == 200
        assert response.json == 'Hello anonymous, access authorized!'
        response = self._get_private_content(case_num=1)
        assert response.status_code == 200
        assert response.json == 'Hello anonymous, access authorized!'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthDemoModesEnabled], indirect=True)
    def test_views_auth_demo_modes_enabled(self):
        # app context is not satisfied
        assert not is_auth_enabled()
        with self.app.app_context():
            assert not is_auth_enabled()

        # many authentication modes available
        response = self.get_items(extra_uri='modes')
        assert response.status_code == 200
        assert response.json['auth_modes'] == ['JWT', 'CERTIFICATE']

        # Get private content (access refused)
        response = self._get_private_content()
        assert response.status_code == 401
        # WWW-Authenticate header is present to indicate the auth mode to use
        assert 'WWW-Authenticate' in response.headers

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthDemoModesEnabled], indirect=True)
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupant_users': True}], indirect=True)
    def test_views_auth_demo_jwt_login(self, init_db_data):
        # retrieve database informations
        login_id, clear_pwd = init_db_data['occupant_users'][0]

        # try to log in
        response = self.post_item(
            login_id=login_id, password=clear_pwd, extra_uri='jwt')
        assert response.status_code == 200
        access_token = response.json['access_token']
        set_cookie = response.headers.get('set-cookie', 'no set cookie')
        cookie_session_data = self._extract_cookie_session(set_cookie)

        # Get some protected datas (access_token)
        response = self._get_private_content(access_token=access_token)
        assert response.status_code == 200
        assert 'Hello' in response.json
        assert 'access granted' in response.json
        assert login_id in response.json
        # roles required
        # user roles does not match
        response = self._get_private_content(
            case_num=0, access_token=access_token)
        assert response.status_code == 403

        # Get some protected datas (session cookie), it also works!
        response = self._get_private_content(cookie_data=cookie_session_data)
        assert response.status_code == 200
        assert 'Hello' in response.json
        assert 'access granted' in response.json
        assert login_id in response.json

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthDemoModesEnabled], indirect=True)
    def test_views_auth_demo_cert_login(self, certificate_data):
        # try to log in
        response = self.post_item(
            extra_uri='cert', headers={'SSL_CLIENT_S_DN': certificate_data})
        assert response.status_code == 200
        set_cookie = response.headers['set-cookie']
        cookie_session_data = self._extract_cookie_session(set_cookie)

        # Get private content (through authentication)
        response = self._get_private_content(cookie_data=cookie_session_data)
        assert response.status_code == 200
        assert 'Hello' in response.json
        assert 'access granted' in response.json
        assert 'bemsvrapp-cleaning-timeseries' in response.json
        # roles required
        # user roles does not match
        response = self._get_private_content(
            case_num=0, cookie_data=cookie_session_data)
        assert response.status_code == 403
        # user roles does match
        response = self._get_private_content(
            case_num=1, cookie_data=cookie_session_data)
        assert response.status_code == 200
