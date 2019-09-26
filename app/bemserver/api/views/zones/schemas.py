"""Api zones module schemas"""

# pylint: disable=too-few-public-methods

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ....models import Zone


class ZoneSchema(ObjectSchema):
    """Zone description, as a building part"""

    _OBJ_CLS = Zone

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(  # pylint: disable=invalid-name
        required=True,
        dump_only=True,
        description='The unique identifier (UUID) of the zone.'
    )
    name = ma.fields.String(
        required=True,
        description='A name (short) for the zone.'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='A description of the zone.'
    )
    zones = ma.fields.List(
        ma.fields.UUID(
            description='A zone ID',
        ),
        missing=list,
        description='A list of zones UUID contained in the current zone.',
    )
    spaces = ma.fields.List(
        ma.fields.UUID(
            description='A space ID',
        ),
        missing=list,
        description='A list of spaces ID contained in the current zone.',
    )
    building_id = ma.fields.UUID(
        required=True,
        description='The UUID of the building to which the zone is associated.'
    )


##########
# Schemas for API query parameters or request body

class ZoneQueryArgsSchema(ma.Schema):
    """Query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Filter by zone name'
    )
    building_id = ma.fields.UUID(
        description='Filter by the building UUID of the zone.'
    )


class ZoneRequestBodySchema(ZoneSchema):
    """Zone post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)


##########
# Schema for API responses

class ZoneHateoasSchema(ma_hateoas.Schema):
    """Zone hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links', '_embedded',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor('zones.ZonesById', zone_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='zones.Zones'),
        'building': ma_hateoas.URLFor(
            endpoint='buildings.BuildingsById', building_id='<building_id>'),
    }, description='HATEOAS resource links')

    # TODO: see what is possible here
    # _embedded = ma_hateoas.Hyperlinks(schema={
    #     'spaces': {
    #         '_links': {
    #             'collection': ma_hateoas.URLFor(
    #                 endpoint='spaces.Spaces', zone_id='<id>')
    #         }
    #     },
    #     'zones': {
    #         '_links': {
    #             'collection': ma_hateoas.URLFor(
    #                 endpoint='zones.Zones', zone_id='<id>')
    #         }
    #     },
    # }, description='HATEOAS embedded resources links')


@rest_api.definition('Zone')
class ZoneSchemaView(ZoneSchema, ZoneHateoasSchema):
    """Zone schema for api views, with hateoas"""

    class Meta(ZoneHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = ZoneHateoasSchema.Meta.dump_only + ('id',)


##########
# Schema for API etag feature

class ZoneEtagSchema(ZoneSchema):
    """Zone schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
