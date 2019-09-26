"""Api services module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.schemas import ObjectSchema

from ....models import Service

# from ....database.db_enums import DBEnumHandler


# TODO: do a validator?
# def validate_kind(value):
#     """Validate a input kind."""
#     dbhandler = DBEnumHandler()
#     service_types = dbhandler.get_service_types()
#     service_type_names = service_types.get_names()
#     if value not in service_type_names:
#         raise ma.ValidationError('Unknown service type.')


@rest_api.definition('Service')
class ServiceSchema(ObjectSchema):
    """Service schema"""

    _OBJ_CLS = Service

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        dump_only=True,
        description='Service ID'
    )
    name = ma.fields.String(
        required=True,
        description='Name of the service'
    )
    description = ma.fields.String(
        description='Description of the service.',
    )
    url = ma.fields.Url(
        description='The URL to call the service',
    )
    model_ids = ma.fields.List(
        ma.fields.UUID(),
        dump_only=True,
    )
    has_frontend = ma.fields.Boolean(
        description='''Indicates whether the module has a frontend. If True, the
            url can be used for display purpose within the Hit2Gap portal'''
    )
    site_ids = ma.fields.List(
        ma.fields.UUID(),
        description='''The list of sites on which the module is installed.
            Sites are identified with their UUIDs''',
        required=True,
    )


class ServiceQueryArgsSchema(ma.Schema):
    """Service get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Service name'
    )
    site = ma.fields.String(
        description='''Site ID. Used to filter by sites on which modules are
            installed'''
    )
    kind = ma.fields.String(
        description='''Specifies a module kind'''
    )
    has_frontend = ma.fields.Boolean(
        description='''Set to True (resp. False) to select modules that come
            (resp. have not) a frontend'''
    )
