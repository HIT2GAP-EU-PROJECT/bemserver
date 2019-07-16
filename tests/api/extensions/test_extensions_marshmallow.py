"""Tests for marshmallow extensions"""

from tests import TestCore

import pytest

import marshmallow as ma

from h2g_platform_core.api.extensions.marshmallow.fields import StringList


class StrList:
    def __init__(self, strings):
        self.strings = strings


class TestApiExtensionsMarshmallow(TestCore):
    """Marshmallow extensions tests"""

    def test_marshmallow_extensions_string_field(self):
        """Test marshmallow custom StringField"""
        field = StringList()

        obj = StrList('')
        assert field.serialize('strings', obj) == []
        obj = StrList('"abc";"def";"ghi"')
        assert field.serialize('strings', obj) == ['abc', 'def', 'ghi']

        assert field.deserialize([]) == ''
        assert field.deserialize(['abc', 'def', 'ghi']) == '"abc";"def";"ghi"'

        with pytest.raises(ma.ValidationError):
            assert field.deserialize(['ab;c', 'def', 'ghi'])
