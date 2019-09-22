"""Api JWT auth module schemas."""

import marshmallow as ma

from ....extensions.rest_api import rest_api


##########
# Schemas for API query parameters or request body

class JWTLoginBodySchema(ma.Schema):
    """JWT login post request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        load_only = ('login_id', 'password',)

    login_id = ma.fields.String(
        required=True,
        description='JWT authentication login ID'
    )
    password = ma.fields.String(
        required=True,
        description='JWT authentication password'
    )


##########
# Schema for API responses

@rest_api.definition('JWTLogin')
class JWTLoginSchemaView(ma.Schema):
    """JWT login schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    access_token = ma.fields.String(
        dump_only=True,
        description='JWT authentication token'
    )
