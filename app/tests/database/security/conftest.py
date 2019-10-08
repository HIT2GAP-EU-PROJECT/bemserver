"""Fixtures for database security manager tests"""

import os
import pytest

from bemserver.database.security.security_manager import (
    SecurityManager, UserAccount)


@pytest.fixture
def gen_user_accounts(tmpdir):
    module_users_data = [
        {'uid': 'bemsvrapp-input-owm', 'pwd': None, 'user_type': 'machine',
         'roles': ['module_data_provider'], 'sites': ['*']},
        {'uid': 'bemsvrapp-cleaning-timeseries', 'pwd': None,
         'user_type': 'machine', 'roles': ['module_data_processor'],
         'sites': ['*']},
        {'uid': 'multi-site', 'pwd': None, 'user_type': 'user',
         'roles': ['building_manager'], 'sites': ['site1', 'site2']},
        {'uid': 'app-mono-site', 'pwd': None, 'user_type': 'machine',
         'roles': ['module_data_processor'], 'sites': ['site4']},
    ]

    # create user accounts
    module_uaccs = {}
    for u_data in module_users_data:
        uacc = UserAccount(**u_data)
        uacc._password = u_data['pwd']
        module_uaccs[uacc.uid] = uacc

    # init security storage folder
    security_dir = tmpdir / 'security'
    if not security_dir.exists():
        os.mkdir(str(security_dir))
    uacc_filepath = security_dir / SecurityManager._USER_ACCOUNTS_FILE

    # store user accounts in file
    SecurityManager.save_to_file(str(uacc_filepath), module_uaccs)

    # return security storage directory
    return str(security_dir)
