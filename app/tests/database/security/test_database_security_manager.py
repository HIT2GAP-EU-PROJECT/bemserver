"""Tests on database security manager (stub)."""

import pytest

from bemserver.database.security.security_manager import (
    SecurityManager, UserAccount)
from bemserver.database.security.exceptions import (
    UserAccountAlreadyExistError)
from bemserver.database.exceptions import ItemNotFoundError

from tests import TestCoreDatabase


class TestDatabaseSecurityManager(TestCoreDatabase):

    def test_database_security_manager_user_account(self):

        uacc = UserAccount('u_name', ['chuck'])
        assert uacc.uid == uacc.name == uacc.login_id == 'u_name'
        assert uacc.roles == ['chuck']
        assert uacc.type == 'user'
        assert uacc.sites == ['*']
        assert uacc.enabled
        assert uacc.has_roles(['chuck'])
        # a root (Chuck Norris) can do anything
        assert uacc.has_roles(['module_data_provider'])
        assert uacc.has_roles(['building_manager', 'module_data_processor'])
        assert uacc.get_identity() == {
            'uid': 'u_name', 'roles': ['chuck'], 'type': 'user'}
        assert not uacc.is_occupant
        assert uacc.verify_scope(sites=['here'])
        assert uacc.verify_scope(sites=['anywhere'])
        assert uacc.verify_scope(sites=['here', 'anywhere'])

        uacc = UserAccount(
            'm_name', ['module_data_provider', 'building_manager'],
            user_type='machine', sites=['here'])
        assert uacc.name == 'm_name'
        assert uacc.roles == ['module_data_provider', 'building_manager']
        assert uacc.type == 'machine'
        assert uacc.sites == ['here']
        assert uacc.enabled
        assert uacc.has_roles(['module_data_provider'])
        assert not uacc.has_roles(['module_data_provider'], strict=True)
        assert uacc.has_roles(['module_data_provider', 'building_manager'])
        assert uacc.has_roles(
            ['module_data_provider', 'building_manager'], strict=True)
        assert uacc.has_roles(
            ['module_data_provider', 'module_data_processor'])
        assert not uacc.has_roles(
            ['module_data_provider', 'module_data_processor'], strict=True)
        assert not uacc.has_roles(['chuck', 'module_data_processor'])
        assert not uacc.has_roles(
            ['chuck', 'module_data_processor'], strict=True)
        assert uacc.get_identity() == {
            'uid': 'm_name',
            'roles': ['module_data_provider', 'building_manager'],
            'type': 'machine',
        }
        assert not uacc.is_occupant
        assert uacc.verify_scope(sites=['here'])
        assert not uacc.verify_scope(sites=['anywhere'])
        assert not uacc.verify_scope(sites=['here', 'anywhere'])

        # password management
        uacc = UserAccount('u_name', ['building_manager'])
        assert uacc.password is None
        uacc.password = 'a_new_pwd'
        assert uacc.password is not None
        assert uacc.password != 'a_new_pwd'  # password is stored crypted
        assert uacc.verify_password('a_new_pwd')
        uacc.password = None
        assert uacc.password is None
        assert not uacc.verify_password('a_new_pwd')
        assert not uacc.verify_password(None)

        # errors
        uacc = UserAccount('u_name', ['module_data_processor'])
        with pytest.raises(ValueError):
            uacc.has_roles('bad_roles_format')
        with pytest.raises(ValueError):
            uacc.has_roles(['bad_role_name'])
        with pytest.raises(ValueError):
            UserAccount('u_name', 'bad_roles_format')
        with pytest.raises(ValueError):
            UserAccount('u_name', ['bad_role_name'])
        with pytest.raises(ValueError):
            UserAccount('u_name', ['chuck'], user_type='bad_type')
        uacc.sites = ['siteA', 'siteB', 'siteC']
        with pytest.raises(ValueError):
            uacc.verify_scope()
        with pytest.raises(TypeError):
            uacc.verify_scope(sites=42)

    def test_database_security_manager(self, gen_user_accounts):

        security_dir = gen_user_accounts
        security_mgr = SecurityManager(security_dir)

        assert security_dir in str(security_mgr.uacc_filepath)
        assert security_dir in str(security_mgr.occ_uacc_filepath)

        uacc = security_mgr.get('bemsvrapp-input-owm')
        assert isinstance(uacc, UserAccount)
        # shortcut to UserAccount has_roles
        assert security_mgr.has_roles(
            'bemsvrapp-input-owm', ['module_data_provider'])

        # create an account
        new_uacc = security_mgr.add_account('leguman', ['chuck'])
        assert new_uacc.uid == 'leguman'
        assert new_uacc.has_roles(['chuck'], strict=True)

        # disable account
        assert new_uacc.enabled
        security_mgr.disable_account('leguman')
        uacc = security_mgr.get('leguman')
        assert not uacc.enabled

        # errors
        # get not found
        with pytest.raises(ItemNotFoundError):
            security_mgr.get('unknown')
        # create while uid already exists
        with pytest.raises(UserAccountAlreadyExistError):
            security_mgr.add_account('leguman', ['building_manager'])
        # create with bad roles
        with pytest.raises(ValueError):
            security_mgr.add_account('professor_chaos', ['bad'])
        # disable an account that does not exist
        with pytest.raises(ItemNotFoundError):
            security_mgr.disable_account('the_invisible_man')

    def test_database_security_manager_occupant_users(self, tmpdir):

        security_mgr = SecurityManager(str(tmpdir))

        # no occupant user accounts
        assert len(security_mgr.occ_user_accounts) == 0

        # create an occupant account
        uacc, uacc_pwd = security_mgr.create_occupant()
        assert len(security_mgr.occ_user_accounts) == 1
        assert uacc.verify_password(uacc_pwd)
        assert uacc.has_roles(['anonymous_occupant'])
        assert uacc.is_occupant

        # create another occupant account
        uacc, uacc_pwd = security_mgr.create_occupant(
            uid='gandalf', pwd='none_shall_pass')
        assert len(security_mgr.occ_user_accounts) == 2
        assert uacc.uid == 'gandalf'
        assert uacc_pwd == 'none_shall_pass'
        assert uacc.verify_password('none_shall_pass')
        assert uacc.has_roles(['anonymous_occupant'])

        # update account password
        security_mgr.update_pwd(uacc.uid, new_pwd='Mithrandir')
        uacc = security_mgr.get('gandalf')
        assert not uacc.verify_password('none_shall_pass')
        assert uacc.verify_password('Mithrandir')
        assert uacc.is_occupant

        # disable account
        assert uacc.enabled
        security_mgr.disable_account(uacc.uid)
        assert not uacc.enabled
        uacc = security_mgr.get('gandalf')
        assert not uacc.enabled
        assert uacc.is_occupant

        # reload security manager
        #  and verify account still exist, updated and disabled
        security_mgr = SecurityManager(str(tmpdir))
        assert len(security_mgr.occ_user_accounts) == 2
        uacc = security_mgr.get('gandalf')
        assert uacc.uid == 'gandalf'
        assert not uacc.verify_password('none_shall_pass')
        assert uacc.verify_password('Mithrandir')
        assert uacc.has_roles(['anonymous_occupant'])
        assert not uacc.enabled

        # errors
        # add an already existing account
        with pytest.raises(UserAccountAlreadyExistError):
            security_mgr.create_occupant(uid='gandalf')
        # update an account that does not exist
        with pytest.raises(ItemNotFoundError):
            security_mgr.update_pwd('the_invisible_man', new_pwd='yo')
