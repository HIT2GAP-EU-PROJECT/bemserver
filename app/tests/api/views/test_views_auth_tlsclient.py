"""Tests for api certificate auth views"""

import datetime as dt
import time
import pytest

from tests import TestCoreApi
from tests.api.views.conftest import TestingConfigAuthCertificateEnabled


class TestingConfigAuthCertExp(TestingConfigAuthCertificateEnabled):
    """App config to test authentication cookie expiration"""
    PERMANENT_SESSION_LIFETIME = dt.timedelta(seconds=1)


@pytest.mark.usefixtures('init_app')
class TestApiViewsAuthCertificate(TestCoreApi):
    """Certificate auth api views tests"""

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

    def _auth_cert_login(self, cert_data=None):
        headers = None
        if cert_data is not None:
            headers = {'SSL_CLIENT_S_DN': cert_data}
        return self.post_item(extra_uri='cert', headers=headers)

    def _extract_cookie_session(self, set_cookie):
        for set_cookie_part in set_cookie.split(';'):
            if 'session=' in set_cookie_part:
                return set_cookie_part.strip()
        return None

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    def test_views_auth_cert_login(self, certificate_data):
        """Test certificate login api endpoint"""
        # try to sign in
        response = self._auth_cert_login(certificate_data)
        assert response.status_code == 200
        assert response.json == {
            'uid': 'bemsvrapp-cleaning-timeseries', 'type': 'machine',
            'roles': ['module_data_processor']}

        # verify authentication cookie
        assert 'set-cookie' in response.headers
        set_cookie = response.headers['set-cookie']
        assert set_cookie is not None
        cookie_session_data = self._extract_cookie_session(set_cookie)
        assert cookie_session_data is not None
        assert 'session=' in cookie_session_data

        # Errors
        # no certificate
        response = self._auth_cert_login()
        assert response.status_code == 422
        # bad certificate
        response = self._auth_cert_login()
        assert response.status_code == 422
        # unknown certificate name (CN)
        response = self._auth_cert_login('CN=unknown')
        assert response.status_code == 404

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_auth_cert_protected_resources(self, certificate_data):
        """Test protected resources access with a certificate."""
        # Get some protected data while not authenticated
        response = self._get_protected_resources()
        assert response.status_code == 401

        # try to sign in
        response = self._auth_cert_login(certificate_data)
        assert response.status_code == 200
        cookie_session_data = self._extract_cookie_session(
            response.headers['set-cookie'])

        # Get some protected datas, now authenticated
        response = self._get_protected_resources(cookie_session_data)
        assert response.status_code == 200

        # Get some protected datas errors
        # a non-authenticated user can not have access to protected datas
        response = self._get_protected_resources()
        assert response.status_code == 401
        # WWW-Authenticate header is present to indicate the auth mode to use
        assert 'WWW-Authenticate' in response.headers

    @pytest.mark.slow
    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertExp], indirect=True)
    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_auth_cert_expiration(self, certificate_data):
        """Test authentication with an expired cookie"""
        # try to sign in
        response = self._auth_cert_login(certificate_data)
        assert response.status_code == 200
        cookie_session_data = self._extract_cookie_session(
            response.headers['set-cookie'])

        # Get protected datas
        response = self._get_protected_resources(cookie_session_data)
        assert response.status_code == 200

        # Wait until access_token has expired (>1 seconds)
        time.sleep(2)

        # Get protected datas
        response = self._get_protected_resources(cookie_session_data)
        # token has expired...
        assert response.status_code == 401
