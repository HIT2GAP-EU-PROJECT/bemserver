"""Api floors module schemas"""

# pylint: disable=too-few-public-methods

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ..schemas import SpatialInfoSchema

from ....models import Floor

from ....database.db_enums import DBEnumHandler


def validate_kind(value):
    """Validate a input floor type."""
    dbhandler = DBEnumHandler()
    floor_types = dbhandler.get_floor_types()
    floor_type_names = floor_types.get_names()
    if value not in floor_type_names:
        raise ma.ValidationError('Unknown floor type.')


class FloorSchema(ObjectSchema):
    """Floor schema"""

    _OBJ_CLS = Floor

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        required=True,
        dump_only=True,
        description='Thee unique indentifier (UUID) of the floor.'
    )
    name = ma.fields.String(
        required=True,
        description='A name (short) associated to the floor'
    )
    kind = ma.fields.String(
        required=True,
        validate=validate_kind,
        description='''A type associated to the floor. See
            /api-docs/redoc#tag/floors/paths/\\~1floors\\~1types\\~1/get for
            the full list of available types, and use the value in the
            `name` field.'''
    )
    level = ma.fields.Integer(
        required=True,
        validate=ma.validate.Range(min=-10, max=150),
        description='Floor level number.'
    )
    spatial_info = ma.fields.Nested(
        SpatialInfoSchema,
        description='Floor spatial information.'
    )
    building_id = ma.fields.UUID(
        required=True,
        description='The UUID of the building in which the floor is located.'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='A description of the floor.'
    )


##########
# Schemas for API query parameters or request body

class FloorQueryArgsSchema(ma.Schema):
    """Floor get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Filter by floor name'
    )
    kind = ma.fields.String(
        validate=validate_kind,
        description='Filter by floor type'
    )
    building_id = ma.fields.UUID(
        description='Filter by the UUID of the associated building.'
    )


class FloorRequestBodySchema(FloorSchema):
    """Floor post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id', 'spatial_info.id',)


##########
# Schema for API responses

class FloorHateoasSchema(ma_hateoas.Schema):
    """Floor hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links', '_embedded',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='floors.FloorsById', floor_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='floors.Floors'),
        'parent': ma_hateoas.URLFor(
            endpoint='buildings.BuildingsById', building_id='<building_id>'),
        'kinds': ma_hateoas.URLFor(endpoint='floors.FloorTypes'),
        # TODO: write this endpoint
        # 'distance_units': ma_hateoas.URLFor(
        #     endpoint='distanceunits.distanceunits'),
    }, description='HATEOAS resource links')

    _embedded = ma_hateoas.Hyperlinks(schema={
        'spaces': {
            '_links': {
                'collection': ma_hateoas.URLFor(
                    endpoint='spaces.Spaces', floor_id='<id>')
            }
        },
    }, description='HATEOAS embedded resources links')


@rest_api.definition('Floor')
class FloorSchemaView(FloorSchema, FloorHateoasSchema):
    """Floor schema for api views, with hateoas"""

    class Meta(FloorHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = FloorHateoasSchema.Meta.dump_only + ('id',)


##########
# Schema for API etag feature

class FloorEtagSchema(FloorSchema):
    """Floor schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
