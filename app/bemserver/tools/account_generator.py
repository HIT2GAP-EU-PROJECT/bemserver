"""Tool to generate account login ids or passwords"""

import string
from random import sample


def _gen_random_str(str_length, available_chars=None):
    if available_chars is None:
        available_chars = string.ascii_letters + string.digits
    return ''.join(sample(available_chars, str_length))


def generate_login_id(prefix=None, suffix=None, sep='_', random_length=4):
    """Generates randomly a new login id"""
    random_part = _gen_random_str(str_length=random_length)
    sep = '' if sep is None else str(sep)
    prefix = '' if prefix is None else str(prefix)
    suffix = '' if suffix is None else str(suffix)
    if len(prefix) > 0:
        prefix = '{}{}'.format(prefix, sep)
    if len(suffix) > 0:
        suffix = '{}{}'.format(sep, suffix)
    return ''.join([prefix, random_part, suffix])


def generate_pwd(pwd_length=12):
    """Generates randomly a new password"""
    return _gen_random_str(str_length=pwd_length)
