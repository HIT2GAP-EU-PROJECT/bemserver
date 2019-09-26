"""Tests for crypto tools"""

from bemserver.tools.crypto import encrypt, check_encryption

from tests import TestCoreTools


class TestToolsCrypto(TestCoreTools):
    """Crypto tool tests"""

    def test_tools_crypto_encrypt(self):
        """Test encryption"""

        salt_or_pepper = bytes('salt_or_pepper', 'utf-8')

        expected_encryption = (
            '$28$73616c745f6f725f70657070657252e6043b53a09e2725a8e12b04f60b83e'
            'b9bdd4544184b5ccc98b9dc878d5c0865a26743da91822882db461162326775d3'
            '68b7f570a3461a12e8bac699426e0e')

        encrypted_data = encrypt('yolo', salt=salt_or_pepper)
        assert encrypted_data == expected_encryption

    def test_tools_crypto_check_encryption(self):
        """Test check encryption (compare clear and encrypted values)"""

        salt_or_pepper = bytes('salt_or_pepper', 'utf-8')

        encrypted_data = encrypt('yolo')
        assert check_encryption('yolo', encrypted_data)
        assert not check_encryption('yoloooo', encrypted_data)

        encrypted_data = encrypt('yolo', salt=salt_or_pepper)
        assert check_encryption('yolo', encrypted_data)
        assert not check_encryption('yoloooo', encrypted_data)
