"""Security manager (user identity, roles...)."""

from contextlib import contextmanager
import threading
import csv
from pathlib import Path

from bemserver.database.exceptions import ItemNotFoundError
from bemserver.tools import crypto
from bemserver.tools.account_generator import (
    generate_login_id, generate_pwd)

from .exceptions import UserAccountAlreadyExistError


@contextmanager
def locked_store(file_path, *, mode='r', **kwargs):
    """Open a user account file storage with a lock to prevent corruptions."""
    with threading.Lock():
        with open(str(file_path), mode, **kwargs) as csvfile:
            yield csvfile
            csvfile.flush()


def _conv_bool(val):
    if val is None:
        return False
    return str(val).lower() in ['true', '1', 't', 'yes', 'y']


def _str_or_none(val):
    return None if val == '' else str(val)


def _str_to_list_or_default(val, *, default=None):
    return default if val in [None, ''] else val.split(',')


class UserAccount():
    """A user account descriptor."""
    def __init__(self, uid, roles, *, pwd=None, user_type='user', sites=['*']):
        """
        :param str uid: The unique ID (user name, ...) of the user account.
        :param list|tuple roles: A list of valid roles for the user.
        :param str pwd: (optional, default None)
            The (clear) password to protect the user account.
        :param str user_type: (optional, default None)
            The type of user account targeted (user or machine).
        :param list sites: (optional, default ['*'])
            A list of site (unique) names/IDs attached to the user account.
        """
        if not self._check_roles(roles):
            raise ValueError(
                'Invalid roles: {}. Available are: {}'.format(
                    roles, SecurityManager.AVAILABLE_ROLES))

        if not self._check_type(user_type):
            raise ValueError(
                'Invalid user type: {}. Available are: {}'.format(
                    user_type, SecurityManager.AVAILABLE_TYPES))

        self.uid = uid
        self._password = None
        self.password = pwd  # use setter to encrypt the password
        self.roles = roles
        self.type = user_type
        self.enabled = True
        self.sites = sites  # for permissions purpose

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'uid="{self.uid}"'
            ', roles={self.roles}'
            ', type="{self.type}"'
            ', enabled={self.enabled}'
            ', sites="{self.sites}"'
            ')'.format(self=self))

    @property
    def name(self):
        """Get user's unique ID (as user name)."""
        return self.uid

    @property
    def login_id(self):
        """Get user's unique ID (as login_id)."""
        return self.uid

    @property
    def password(self):
        """Get user's password"""
        return self._password

    @password.setter
    def password(self, value):
        """Set password with a clear value which is immediatly hashed."""
        try:
            if value is not None:
                self._password = crypto.encrypt(value)
            else:
                # erase the old password
                self._password = None
        except (TypeError, ValueError) as exc:
            raise ValueError('Invalid password: {}'.format(str(exc)))

    @property
    def is_occupant(self):
        """Return True if user account is an occupant
        (is not 'root' and has anonymous_occupant role).
        """
        return (not self.has_roles(['chuck'])
                and self.has_roles(['anonymous_occupant']))

    @staticmethod
    def _check_roles(roles):
        if not isinstance(roles, (list, tuple,)):
            return False
        for role in roles:
            if role not in SecurityManager.AVAILABLE_ROLES:
                return False
        return True

    @staticmethod
    def _check_type(user_type):
        return user_type in SecurityManager.AVAILABLE_TYPES

    def has_roles(self, roles_required, *, strict=False):
        """Verify if a user has 'roles_required' in his roles.

        :param list|tuple roles_required: A list of valid roles required.
        :param bool strict:
            Verify if roles_required is strictly equal to user account roles.
        :return bool: True if user's roles are enough for requirement.
        :raises ValueError: When invalid required roles are passed.
        """
        if not self._check_roles(roles_required):
            raise ValueError(
                'Invalid roles required: {}. Available are: {}'.format(
                    roles_required, SecurityManager.AVAILABLE_ROLES))
        # verify that user roles exactly match with required
        if strict:
            return self.roles == roles_required
        # a root (Chuck Norris) can do anything
        if 'chuck' in self.roles:
            return True
        # verify that user has every required role
        for role_req in roles_required:
            if role_req in self.roles:
                return True
        return False

    def verify_password(self, value):
        """Compare input password with hashed password.

        :param str value: The input password to verify.
        :return bool: True if input password match with stored one.
        """
        try:
            return crypto.check_encryption(value, self.password)
        except (TypeError, ValueError):
            return False

    def get_identity(self):
        """Return authentication identity.

        :return dict: Identity data that is json serializable.
        """
        return {
            'uid': self.uid,
            'roles': self.roles,
            'type': self.type,
        }

    def verify_scope(self, *, sites=None):
        """Verify user's permissions.

        :param list sites: (optional, default None)
            List of site unique IDs (names) for which user access is verified.
        :return bool: True if authorized, else False.
        :raise ValueError: When sites is not defined.
        """
        if sites is None:
            raise ValueError('Sites parameter is not defined!')
        if '*' in self.sites:
            return True
        for site in sites:
            if str(site) not in self.sites:
                return False
        return True


class SecurityManager():
    """The security manager allows to store, retrieve and verify the
    validity of user accounts.
    """

    AVAILABLE_TYPES = ['user', 'machine']
    AVAILABLE_ROLES = [
        'chuck', 'module_data_provider', 'module_data_processor',
        'building_manager', 'anonymous_occupant',
    ]

    _USER_ACCOUNTS_FILE = 'user_accounts.csv'
    _OCC_USER_ACCOUNTS_FILE = 'occ_user_accounts.csv'

    def __init__(self, dir_path):
        """
        :param str|Path dir_path:
            Path of the folder where user accounts are stored.
        :raise ValueError: When invalid occupant user account storatge file.
        """
        self._dir_path = Path(dir_path)
        if not self._dir_path.exists() or not self._dir_path.is_dir():
            raise ValueError(
                'Invalid user account storage directory: {}'
                .format(str(dir_path)))

        self.user_accounts = self.load_from_file(self.uacc_filepath)
        self.occ_user_accounts = self.load_from_file(self.occ_uacc_filepath)

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'user_accounts={uacc_count}'
            ', occ_user_accounts={occ_uacc_count}'
            ')'.format(
                self=self, uacc_count=len(self.user_accounts),
                occ_uacc_count=len(self.occ_user_accounts)))

    @property
    def uacc_filepath(self):
        """Return user accounts file path."""
        return self._dir_path / self._USER_ACCOUNTS_FILE

    @property
    def occ_uacc_filepath(self):
        """Return occupant user accounts file path."""
        return self._dir_path / self._OCC_USER_ACCOUNTS_FILE

    def _get_occ_user_account(self, uid, *, raise_error=False):
        try:
            return self.occ_user_accounts[uid]
        except KeyError:
            if raise_error:
                raise ItemNotFoundError('"{}" user not found!'.format(uid))
        return None

    def _save(self, uacc):
        # save user account in the appropriate file storage
        # occupant user account case
        if uacc.is_occupant:
            self.occ_user_accounts[uacc.uid] = uacc
            self.save_to_file(self.occ_uacc_filepath, self.occ_user_accounts)
        # default case
        else:
            self.user_accounts[uacc.uid] = uacc
            self.save_to_file(self.uacc_filepath, self.user_accounts)

    def get(self, uid, *, raise_error=True):
        """Return the user account (if exists).

        :param str uid: The unique ID (login ID, user name, ...) to search.
        :return UserAccount: An instance of UserAccount.
        :raises ItemNotFoundError: When user name does not exist.
        """
        try:
            return self.user_accounts[uid]
        except KeyError:
            return self._get_occ_user_account(uid, raise_error=raise_error)
        return None

    def add_account(
            self, uid, roles, *, pwd=None, user_type='user', sites=['*']):
        """Create a new user account.

        :param str uid: The unique ID (login ID, name, ...) of the account.
        :param list|tuple roles: A list of valid roles for the user.
        :param str pwd: (optional, default None)
            The (clear) password to protect the user account.
        :param str user_type: (optional, default None)
            The type of user account targeted (user or machine).
        :param list sites: (optional, default ['*'])
            The list of unique site names/IDs attached to the user account.
        :return UserAccount: The instance of user account created.
        :raise UserAccountAlreadyExistError: When uid already exist.
        """
        # uid already exists?
        if self.get(uid, raise_error=False) is not None:
            raise UserAccountAlreadyExistError(
                '"{}" user already exist!'.format(uid))
        # create user account
        new_uacc = UserAccount(
            uid, roles, pwd=pwd, user_type=user_type, sites=sites)
        # save account in storage
        self._save(new_uacc)
        return new_uacc

    def create_occupant(self, *, uid=None, pwd=None, sites=['*']):
        """Shortcut to create a new occupant user account.

        :param str uid: (optional, default None)
            The unique ID (login ID, ...) of the occupant account.
            If None, a unique random login ID is generated.
        :param str pwd: (optional, default None)
            The password for the occupant user account.
            If None, a random password is generated.
        :param list sites: (optional, default ['*'])
            The list of unique site names/IDs attached to the user account.
        :return tuple: The instance of occupant UserAccount created
            and its (clear) password. (UserAccount, clear_pwd)
        :raise UserAccountAlreadyExistError: When uid already exist.
        """
        new_uid = uid or generate_login_id()
        if uid is not None:
            if self._get_occ_user_account(uid) is not None:
                raise UserAccountAlreadyExistError(
                    '"{}" occupant user already exist!'.format(uid))
        else:
            # as uid must be unique, search if new generated one already exists
            while self._get_occ_user_account(new_uid) is not None:
                # regenerate a new uid until it is unique...
                new_uid = generate_login_id()
        # now get a random password
        new_pwd = pwd or generate_pwd()
        # then create and save the new account, and also return clear password
        return self.add_account(
            new_uid, ['anonymous_occupant'], pwd=new_pwd, sites=sites), new_pwd

    def update_pwd(self, uid, *, new_pwd=None):
        """Update the password of an existing user account.

        :param str uid: The unique ID (name, login ID, ...) of user account.
        :param str new_pwd: The new (clear) password.
            If None, a (clear) random password is generated (and returned).
        :return str: The new (clear) password.
        :raise ItemNotFoundError: When uacc was not found.
        """
        # search and verify user account existence
        uacc = self.get(uid)
        new_pwd = new_pwd or generate_pwd()
        uacc.password = new_pwd
        # save account in storage
        self._save(uacc)
        # return clear password
        return new_pwd

    def disable_account(self, uid):
        """Disable an existing user account.

        :param str uid: The unique ID (name, login ID, ...) of user account.
        :raise ItemNotFoundError: When uid was not found.
        """
        # search and verify user account existence
        uacc = self.get(uid)
        # nothing to do if account is already disabled
        if uacc.enabled:
            # disable user account
            uacc.enabled = False
            # save account in storage
            self._save(uacc)

    def has_roles(self, uid, roles_required):
        """Verify if a user has 'roles_required' in his roles.

        :param str uid: The unique ID (user name, ...) to search and verify.
        :param list|tuple roles_required: A list of valid roles required.
        :return bool: True if user's roles are enough for requirement.
        :raises ItemNotFoundError: When user name (uid) does not exist.
        :raises ValueError: When invalid required roles are passed.
        """
        uacc = self.get(uid)
        return uacc.has_roles(roles_required)

    @staticmethod
    def load_from_file(file_path):
        """Load user accounts from a CSV file.

        :param str|Path file_path: Path of user accounts CSV file.
        :return dict: A dict containing UserAccount instances.
            (uid as the key and UserAccount instance as value)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {}
        # Load user accounts data
        loaded_uaccs = {}
        with locked_store(str(file_path), newline='') as csvfile:
            for row in csv.DictReader(csvfile, delimiter=';'):
                uacc = UserAccount(
                    row['name'], _str_to_list_or_default(row['roles']),
                    user_type=_str_or_none(row['type']),
                    sites=_str_to_list_or_default(row['sites'], default=[]),
                )
                # /!\ password in storage is already crypted
                uacc._password = _str_or_none(row['pwd'])
                uacc.enabled = _conv_bool(row['enabled'])
                loaded_uaccs[uacc.uid] = uacc
        return loaded_uaccs

    @staticmethod
    def save_to_file(file_path, user_accounts):
        """Save user accounts to a CSV file.

        :param str|Path file_path: Path of user accounts CSV file.
        :param dict user_accounts: A dict containing UserAccount instances.
            (uid as the key and UserAccount instance as value)
        """
        file_path = Path(file_path)
        # Write user accounts data
        with locked_store(str(file_path), mode='w') as csvfile:
            writer = csv.DictWriter(
                csvfile, delimiter=';', fieldnames=[
                    'name', 'pwd', 'type', 'roles', 'enabled', 'sites'])
            writer.writeheader()
            for _, uacc in user_accounts.items():
                uacc_datas = {
                    'name': uacc.uid,
                    'pwd': uacc.password if uacc.password is not None else '',
                    'type': uacc.type,
                    'roles': ','.join(uacc.roles),
                    'enabled': '1' if uacc.enabled else '0',
                    'sites': ','.join(uacc.sites),
                }
                writer.writerow(uacc_datas)
