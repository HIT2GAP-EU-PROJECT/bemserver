"""Api windows module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ..schemas import SurfaceInfoSchema

from ....models import Window
from ....database.db_enums import DBEnumHandler


def validate_covering_kind(value):
    """Validate an input kind."""
    dbhandler = DBEnumHandler()
    dbhandler.get_space_types()
    type_names = dbhandler.get_window_covering_types().get_names()
    if value not in type_names:
        raise ma.ValidationError('Unknown space type.')


def validate_orientation(value):
    """Validate an input kind."""
    dbhandler = DBEnumHandler()
    dbhandler.get_space_types()
    type_names = dbhandler.get_orientation_types().get_names()
    if value not in type_names:
        raise ma.ValidationError('Unknown space type.')


class WindowSchema(ObjectSchema):
    """Window description"""

    _OBJ_CLS = Window

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        required=True,
        dump_only=True,
        description='Window ID'
    )
    name = ma.fields.String(
        required=True,
        description='Window name'
    )
    covering = ma.fields.String(
        validate=validate_covering_kind,
        description='Window covering type code name'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Window description'
    )
    surface_info = ma.fields.Nested(
        SurfaceInfoSchema,
        description='Window\'s spatial informations'
    )
    orientation = ma.fields.String(
        validate=validate_orientation,
        description='Orientation of the window'
    )
    facade_id = ma.fields.UUID(
        required=True,
        description='Window\'s facade ID'
    )
    u_value = ma.fields.Float(
        description='U-value (thermal transmittance)'
    )


##########
# Schemas for API query parameters or request body

class WindowQueryArgsSchema(ma.Schema):
    """Query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Window name'
    )
    covering = ma.fields.String(
        description='Window covering type code name'
    )
    facade_id = ma.fields.UUID(
        description='Window\'s facade ID'
    )


class WindowRequestBodySchema(WindowSchema):
    """Window post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)


##########
# Schema for API responses

class WindowHateoasSchema(ma_hateoas.Schema):
    """Window hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor('windows.WindowsById', window_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='windows.Windows'),
        'parent': ma_hateoas.URLFor(
            endpoint='facades.FacadesById', facade_id='<facade_id>'),
        'kinds': ma_hateoas.URLFor(endpoint='windows.WindowCoveringTypes'),
    }, description='HATEOAS resource links')


@rest_api.definition('Window')
class WindowSchemaView(WindowSchema, WindowHateoasSchema):
    """Window schema for api views"""

    class Meta(WindowHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = WindowHateoasSchema.Meta.dump_only + (
            'id', 'spatial_info.id',)


##########
# Schema for API etag feature

class WindowEtagSchema(WindowSchema):
    """Window schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
