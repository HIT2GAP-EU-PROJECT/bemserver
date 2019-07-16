"""Api auth module schemas."""

import marshmallow as ma

from ...extensions.rest_api import rest_api


##########
# Schema for API responses

@rest_api.definition('AuthenticationModes')
class AuthModesSchemaView(ma.Schema):
    """Authentication modes schema for api views."""

    class Meta:
        """Schema Meta properties"""
        strict = True

    auth_modes = ma.fields.List(
        ma.fields.String,
        dump_only=True,
        description='Available authentication modes'
    )


@rest_api.definition('Indentity')
class IdentitySchemaView(ma.Schema):
    """Identity schema."""
    class Meta:
        strict = True
        dump_only = ('uid', 'type', 'roles',)

    uid = ma.fields.String(
        required=True,
        description='Identity unique ID'
    )
    type = ma.fields.String(
        required=True,
        description='Identity type'
    )
    roles = ma.fields.List(
        ma.fields.String(),
        required=True,
        description='Identity roles',
    )
