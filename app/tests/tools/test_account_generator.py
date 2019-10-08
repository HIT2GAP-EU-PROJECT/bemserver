"""Tests for account login ids and passwords generation tools"""

import pytest
from bemserver.tools.account_generator import (
    _gen_random_str, generate_login_id, generate_pwd)

from tests import TestCoreTools


class TestToolsAccountGenerator(TestCoreTools):
    """Account generator tool tests"""

    def test_tools_gen_random_str(self):
        """Test random string generation"""

        # generate a 4 chars length string
        res = _gen_random_str(4)
        assert len(res) == 4

        # generate a 7 chars length string using a custom available chars list
        res = _gen_random_str(7, available_chars='azerty987')
        assert len(res) == 7
        # assume that unwanted chars are not present
        # ('b' was not in available chars list)
        assert 'b' not in res

        # assume that generator is random enough
        assert _gen_random_str(4) != _gen_random_str(4)

        # Errors:
        # string length is greater than available_chars length
        with pytest.raises(ValueError):
            _gen_random_str(7, available_chars='azerty')

    def test_tools_login_id_gen(self):
        """Test login id generation"""

        # no prefix, no suffix, default separator, default random part length
        login_id_gen = generate_login_id()
        assert len(login_id_gen) == 4

        # no prefix, no suffix, default separator, a custom random part length
        login_id_gen = generate_login_id(random_length=7)
        assert len(login_id_gen) == 7

        # a prefix, no suffix, default separator, default random part length
        login_id_gen = generate_login_id(prefix='user')
        assert login_id_gen.startswith('user_')
        assert len(login_id_gen) == 9

        # no prefix, a suffix, default separator, default random part length
        login_id_gen = generate_login_id(suffix='42')
        assert login_id_gen.endswith('_42')
        assert len(login_id_gen) == 7

        # a prefix, a suffix, default separator, default random part length
        login_id_gen = generate_login_id(prefix='user', suffix='42')
        assert login_id_gen.startswith('user_')
        assert login_id_gen.endswith('_42')
        assert len(login_id_gen) == 12

        # a prefix, a suffix, custom separator, default random part length
        login_id_gen = generate_login_id(prefix='user', suffix='42', sep='-')
        assert login_id_gen.startswith('user-')
        assert login_id_gen.endswith('-42')
        assert len(login_id_gen) == 12

        # a prefix, a suffix, custom separator, default random part length
        login_id_gen = generate_login_id(prefix='user', suffix='42', sep=None)
        assert login_id_gen.startswith('user')
        assert login_id_gen.endswith('42')
        assert len(login_id_gen) == 10

        # Errors:
        # bad length parameter value
        with pytest.raises(TypeError):
            generate_login_id(random_length=None)
        with pytest.raises(TypeError):
            generate_login_id(random_length='wrong')
        with pytest.raises(ValueError):
            generate_login_id(random_length=-1)

    def test_tools_pwd_gen(self):
        """Test password generation"""

        # generate a password, with default length
        pwd_gen = generate_pwd()
        assert len(pwd_gen) == 12

        # generate a password, with a custom length
        pwd_gen = generate_pwd(pwd_length=7)
        assert len(pwd_gen) == 7

        # Errors:
        # bad length parameter value
        with pytest.raises(TypeError):
            generate_pwd(pwd_length=None)
        with pytest.raises(TypeError):
            generate_pwd(pwd_length='wrong')
        with pytest.raises(ValueError):
            generate_pwd(pwd_length=-1)
