"""Tests for user data model"""

from bemserver.models import User

from tests import TestCoreModel


class TestModelUser(TestCoreModel):
    """User model tests"""

    def test_model_user_password(self):
        """Tests password functions"""

        user_data = {
            'email': 'chuck.norris@kicks.asses',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }
        user = User(**user_data)

        # set and check password:
        pwd = 'mawashi'
        # password is currently not set
        assert user.password is None
        assert not user.check_password(pwd)
        # set password
        user.password = pwd
        assert user.check_password(pwd)

    def test_model_user(self):
        """Tests on model create and update"""

        u_first_name = 'Hattori'
        u_last_name = 'Hanzo'
        u_email = 'hanzo@sushi.bar'
        user = User(
            email=u_email, first_name=u_first_name, last_name=u_last_name)
        assert user.full_name == ' '.join([u_first_name, u_last_name])
        assert user.login == u_email
