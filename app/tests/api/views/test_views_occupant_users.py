"""Tests for api anonymous occupant users views."""

import pytest

from tests import TestCoreApi
from tests.api.views.conftest import TestingConfig


class TestingConfigAuthJWTEnabled(TestingConfig):
    """App config to test authentication stuff"""
    AUTHENTICATION_ENABLED = True
    AUTH_JWT_ENABLED = True


@pytest.mark.usefixtures('init_app')
@pytest.mark.parametrize(
    'init_app', [TestingConfigAuthJWTEnabled], indirect=True)
class TestApiViewsOccupantUsers(TestCoreApi):
    """Anonymous occupant users api views tests."""

    base_uri = '/occupant_users/'

    def _occupant_login(self, *, login_id=None, password=None, **kwargs):
        kwargs['uri'] = '/auth/'
        kwargs['extra_uri'] = 'jwt'
        return self.post_item(login_id=login_id, password=password, **kwargs)

    def _get_header_jwt(self, access_token):
        return {'Authorization': 'Bearer {}'.format(access_token)}

    def test_views_occupant_users_generate_account(self):
        """Test generate an occupant account api endpoint"""
        response = self.post_item(**{'extra_uri': 'generate_account'})
        assert response.status_code == 200
        assert 'login_id' in response.json
        assert 'pwd' in response.json

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupant_users': True}], indirect=True)
    def test_views_occupant_users_regenerate_pwd(self, init_db_data):
        """Test regenerate a password for an occupant account api endpoint"""
        # retrieve database informations
        login_id, old_clear_pwd = init_db_data['occupant_users'][0]

        # ask a password regeneration
        response = self.post_item(
            extra_uri='{}/regenerate_pwd'.format(login_id))
        assert response.status_code == 200
        assert 'login_id' in response.json
        assert response.json['login_id'] == login_id
        assert 'pwd' in response.json
        assert response.json['pwd'] != old_clear_pwd

        # ask a password regeneration errors: invalid login_id parameter
        response = self.post_item(extra_uri='bad_id/regenerate_pwd')
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'init_db_data', [{'gen_occupant_users': True}], indirect=True)
    def test_views_occupant_users_change_pwd(self, init_db_data):
        """Test change the password for an occupant account api endpoint"""
        # retrieve database informations
        login_id, clear_pwd = init_db_data['occupant_users'][0]

        # sign in
        response = self._occupant_login(login_id=login_id, password=clear_pwd)
        assert response.status_code == 200
        access_token = response.json['access_token']

        # change the password
        response = self.put_item(
            None, pwd=clear_pwd, new_pwd='new_pwd',
            headers=self._get_header_jwt(access_token),
            extra_uri='{}/change_pwd'.format(login_id))
        assert response.status_code == 200
        assert 'login_id' in response.json
        assert response.json['login_id'] == login_id
        # clear password not returned in response (not like generate account)
        assert 'pwd' not in response.json

        # try to sign in with the new password
        response = self._occupant_login(
            login_id=login_id, password='new_pwd')
        assert response.status_code == 200
