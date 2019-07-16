"""Api anonymous occupant users module schemas."""

import marshmallow as ma

from ...extensions.rest_api import rest_api


##########
# Schemas for API query parameters or request body

class OccupantChangePwdRequestBodySchema(ma.Schema):
    """Occupant change password put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)

    pwd = ma.fields.String(
        required=True,
        attribute='password',
        description='Occupant account password'
    )
    new_pwd = ma.fields.String(
        required=True,
        attribute='new_password',
        description='Occupant account new password'
    )


##########
# Schema for API responses

@rest_api.definition('OccupantAccount')
class OccupantAccountSchemaView(ma.Schema):
    """Occupant account schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id', 'login_id', 'pwd',)

    login_id = ma.fields.String(
        required=True,
        description='Occupant account login ID'
    )
    pwd = ma.fields.String(
        required=True,
        attribute='password',
        description='Occupant account password'
    )
