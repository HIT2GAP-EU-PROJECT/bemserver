"""Tools to encrypt data (password...)"""

from os import urandom
import hashlib
import binascii


HMAC_HASH_DIGEST_ALGO = 'sha512'
ITERATIONS = 100000


def _dub_encryption(salt, hashed_value):
    """Build encrypted value by assembling `salt` and `hashed_value`"""
    hex_salt = binascii.hexlify(salt)
    hex_hash = binascii.hexlify(hashed_value)
    return '${}${}{}'.format(
        len(hex_salt),
        str(hex_salt, 'utf-8'),
        str(hex_hash, 'utf-8')
    )


def _snoop_encryption(encrypted_value):
    """Extract `salt` and `hashed_value` from `encrypted_value`"""
    try:
        _, salt_len, remainder = encrypted_value.split('$')
    except (ValueError, AttributeError):
        raise ValueError('Invalid hash value: {}'.format(encrypted_value))
    return (
        binascii.unhexlify(remainder[:int(salt_len)]),
        binascii.unhexlify(remainder[int(salt_len):]),
    )


def encrypt(value, salt=None):
    """Encrypt a string (e.g. a password)

    Use PBKDF2 with HMAC, SHA-512 and 100000 iterations

    :param str value: string to encrypt (password)
    :param bytes salt: encryption salt

    Return a string containing encrypted salt and value
    """

    b_value = bytes(value, 'utf-8')

    if salt is None:
        salt = urandom(64)

    hashed_value = hashlib.pbkdf2_hmac(
        HMAC_HASH_DIGEST_ALGO, b_value, salt, ITERATIONS)

    return _dub_encryption(salt, hashed_value)


def check_encryption(clear_value, encrypted_value):
    """Compare encryption of a clear value with an ecrypted value

    :param str clear_value: string to check
    :param str encrypted_value: encrypted value

    Return True iif clear_value encryption matches encrypted_value
    """
    salt, _ = _snoop_encryption(encrypted_value)
    return encrypt(clear_value, salt=salt) == encrypted_value
