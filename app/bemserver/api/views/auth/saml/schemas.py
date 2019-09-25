"""Api SAML auth module schemas."""

import marshmallow as ma


##########
# Schemas for API query parameters or request body

class SSOQueryArgsSchema(ma.Schema):
    """SSO query parameters schema."""
    class Meta:
        strict = True

    relay_state = ma.fields.Url(
        description='Relay state URL',
        load_from='RelayState',
        missing=None,
    )


##########
# Schema for API responses

class SSOLoginSchemaView(ma.Schema):
    """SSO login URL schema."""
    class Meta:
        strict = True
        dump_only = ('login_url',)

    login_url = ma.fields.Url(
        required=True,
        description='SSO login URL'
    )
