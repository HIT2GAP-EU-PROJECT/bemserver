"""Data model for user"""

from .thing import Thing
from ..tools import crypto


class User(Thing):
    """User model class"""

    def __init__(self, email, first_name=None, last_name=None, password=None):
        super().__init__()
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self._password = None
        self.password = password

    @property
    def full_name(self):
        """Get user's fullname (first and last name)"""
        return ' '.join([self.first_name, self.last_name])

    @property
    def login(self):
        """Get user's login"""
        # email attribute is used as user login
        return self.email

    @property
    def password(self):
        """Get user's password"""
        return self._password

    @password.setter
    def password(self, value):
        """Set password with a clear value which is immediatly hashed."""
        try:
            # TODO: warn about trying to set with None value?
            if value is not None:
                self._password = crypto.encrypt(value)
        except (TypeError, ValueError) as exc:
            raise ValueError('Invalid password: {}'.format(str(exc)))

    def check_password(self, value):
        """Compare input password with hashed password"""
        try:
            return crypto.check_encryption(value, self.password)
        except (TypeError, ValueError):
            return False
