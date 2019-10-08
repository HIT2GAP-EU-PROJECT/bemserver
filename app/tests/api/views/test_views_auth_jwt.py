"""Tests for api JWT auth views"""

import datetime as dt
import time
from flask_jwt_simple import decode_jwt
import pytest

from tests import TestCoreApi
from tests.api.views.conftest import TestingConfig


class TestingConfigAuthJWTEnabled(TestingConfig):
    """App config to test JWT authentication stuff"""
    AUTHENTICATION_ENABLED = True
    AUTH_JWT_ENABLED = True


class TestingConfigAuthJWTExp(TestingConfigAuthJWTEnabled):
    """App config to test authentication access token expiration"""
    JWT_EXPIRES = dt.timedelta(seconds=1)


@pytest.mark.usefixtures('init_app')
class TestApiViewsAuthJWT(TestCoreApi):
    """JWT auth api views tests"""

    base_uri = '/auth/'

    def _get_protected_resources(self, *, access_token=None, **kwargs):
        kwargs['uri'] = '/occupants/'
        if access_token is not None:
            kwargs['headers'] = self._get_header_jwt(access_token)
        return self.get_items(**kwargs)

    def _auth_jwt_login(self, *, login_id=None, password=None, **kwargs):
        kwargs['extra_uri'] = 'jwt'
        return self.post_item(login_id=login_id, password=password, **kwargs)

    def _get_header_jwt(self, access_token):
        return {'Authorization': 'Bearer {}'.format(access_token)}

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthJWTEnabled], indirect=True)
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupant_users': True}], indirect=True)
    def test_views_auth_jwt_login(self, init_db_data):
        """Test JWT login api endpoint"""
        # retrieve database informations
        login_id, clear_pwd = init_db_data['occupant_users'][0]

        # try to sign in
        response = self._auth_jwt_login(login_id=login_id, password=clear_pwd)
        assert response.status_code == 200
        assert 'access_token' in response.json

        # verify token content
        with self.app.app_context():
            claim = self.app.config['JWT_IDENTITY_CLAIM']
            token = decode_jwt(response.json['access_token'])
            assert 'exp' in token
            assert 'iat' in token
            assert 'nbf' in token
            assert claim in token
            assert token[claim]['uid'] == login_id
            assert token[claim]['roles'] == ['anonymous_occupant']
            assert token[claim]['type'] == 'user'

        # verify authentication cookie
        assert 'set-cookie' in response.headers
        set_cookie = response.headers['set-cookie']
        assert set_cookie is not None
        assert 'session=' in set_cookie

        # Errors
        # no login_id and/or password
        response = self._auth_jwt_login()
        assert response.status_code == 422
        # unknown login_id value
        response = self._auth_jwt_login(login_id='bad_id', password=clear_pwd)
        assert response.status_code == 401
        # bad password
        response = self._auth_jwt_login(login_id=login_id, password='bad_pwd')
        assert response.status_code == 401

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthJWTEnabled], indirect=True)
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupant_users': True}], indirect=True)
    def test_views_auth_jwt_protected_resources(self, init_db_data):
        """Test protected resources access with an occupant account"""
        # retrieve database informations
        login_id, clear_pwd = init_db_data['occupant_users'][0]

        # try to sign in
        response = self._auth_jwt_login(login_id=login_id, password=clear_pwd)
        assert response.status_code == 200
        access_token = response.json['access_token']

        # Get some protected datas
        response = self._get_protected_resources(access_token=access_token)
        assert response.status_code == 200

        # Get some protected datas errors
        # a non-authenticated user can not have access to protected datas
        response = self._get_protected_resources()
        assert response.status_code == 401
        # WWW-Authenticate header is present to indicate the auth mode to use
        assert 'WWW-Authenticate' in response.headers

    @pytest.mark.slow
    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthJWTExp], indirect=True)
    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupant_users': True}], indirect=True)
    def test_views_auth_jwt_expiration(self, init_db_data):
        """Test authentication with an expired JsonWebToken"""
        # retrieve database informations
        login_id, clear_pwd = init_db_data['occupant_users'][0]

        # Login to get token
        response = self._auth_jwt_login(login_id=login_id, password=clear_pwd)
        assert response.status_code == 200
        access_token = response.json['access_token']

        # Get protected datas
        response = self._get_protected_resources(access_token=access_token)
        assert response.status_code == 200

        # Wait until access_token has expired (>1 seconds)
        time.sleep(2)

        # Get protected datas
        response = self._get_protected_resources(access_token=access_token)
        # token has expired...
        assert response.status_code == 401
