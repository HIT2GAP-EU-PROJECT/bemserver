"""Api spaces module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ..schemas import SpatialInfoSchema

from ....models import Space, SpaceOccupancy

from ....database.db_enums import DBEnumHandler


class SpaceOccupancySchema(ObjectSchema):
    """Occupancy description of a space"""

    _OBJ_CLS = SpaceOccupancy

    class Meta:
        """Schema Meta properties"""
        strict = True

    nb_permanents = ma.fields.Integer(
        required=False,
        validate=ma.validate.Range(min=0),
        description='Space occupancy: number of permanent/regular occupants'
    )
    nb_max = ma.fields.Integer(
        required=False,
        validate=ma.validate.Range(min=0),
        description='Space occupancy: maximum number of occupants (capacity)'
    )


def validate_kind(value):
    """Validate an input kind."""
    dbhandler = DBEnumHandler()
    space_types = dbhandler.get_space_types()
    space_type_names = space_types.get_names()
    if value not in space_type_names:
        raise ma.ValidationError('Unknown space type.')


class SpaceSchema(ObjectSchema):
    """Space schema"""

    _OBJ_CLS = Space

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        required=True,
        dump_only=True,
        description='The unique identifier (UUID) of the space.'
    )
    name = ma.fields.String(
        required=True,
        description='The name (short) associated to the space.'
    )
    kind = ma.fields.String(
        # required=True,
        validate=validate_kind,
        description='''The type associated to the space. For a full list of
            possible types, see
            /api-docs/redoc#tag/spaces/paths/\\~1spaces\\~1types\\~1/get.'''
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='A description of the space.'
    )
    occupancy = ma.fields.Nested(
        SpaceOccupancySchema,
        description='Space occupancy information'
    )
    spatial_info = ma.fields.Nested(
        SpatialInfoSchema,
        description='Space spatial information'
    )
    floor_id = ma.fields.UUID(
        required=True,
        description='The UUID of the floor to which the space belongs.'
    )


##########
# Schemas for API query parameters or request body

class SpaceQueryArgsSchema(ma.Schema):
    """Query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Filter by space name'
    )
    kind = ma.fields.String(
        validate=validate_kind,
        description='Filter by space type'
    )
    floor_id = ma.fields.UUID(
        description='Filter by the UUID of a floor.'
    )


class SpaceRequestBodySchema(SpaceSchema):
    """Space post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id', 'occupancy.id', 'spatial_data.id',)


##########
# Schema for API responses

class SpaceHateoasSchema(ma_hateoas.Schema):
    """Space hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links', '_embedded',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor('spaces.SpacesById', space_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='spaces.Spaces'),
        'parent': ma_hateoas.URLFor(
            endpoint='floors.FloorsById', floor_id='<floor_id>'),
    }, description='HATEOAS resource links')

    # _embedded = ma_hateoas.Hyperlinks(schema={
    #     'facades': {
    #         '_links': {
    #             'collection': ma_hateoas.URLFor(
    #                 endpoint='facades.facades', space_id='<id>')
    #         }
    #     }
    # }, description='HATEOAS embedded resources links')


@rest_api.definition('Space')
class SpaceSchemaView(SpaceSchema, SpaceHateoasSchema):
    """Space schema for api views"""

    class Meta(SpaceHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = SpaceHateoasSchema.Meta.dump_only + (
            'id', 'occupancy.id', 'spatial_data.id',)


##########
# Schema for API etag feature

class SpaceEtagSchema(SpaceSchema):
    """Space schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
