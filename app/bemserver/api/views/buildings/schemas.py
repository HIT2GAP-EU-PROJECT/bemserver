"""Api buildings module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ....models import Building

from ....database.db_enums import DBEnumHandler


def validate_kind(value):
    """Validate a input kind."""
    dbhandler = DBEnumHandler()
    building_types = dbhandler.get_building_types()
    building_type_names = building_types.get_names()
    if value not in building_type_names:
        raise ma.ValidationError('Unknown building type.')


class BuildingSchema(ObjectSchema):
    """Building schema"""

    _OBJ_CLS = Building

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        required=True,
        dump_only=True,
        description='A UUID for the building.'
    )
    name = ma.fields.String(
        required=True,
        description='A short building name'
    )
    kind = ma.fields.String(
        required=True,
        validate=validate_kind,
        description='''Building type. See
            /api-docs/redoc#tag/buildings/paths/\\~1buildings\\~1types\\~1/get
            for the full list of possible types, and use the value in the
            `name` field.'''
    )
    area = ma.fields.Float(
        required=True,
        validate=ma.validate.Range(min=0),
        description='Building area in square meter.'
    )
    site_id = ma.fields.UUID(
        required=True,
        description='The UUID of the site to which the building is associated.'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='A description of the building.'
    )


##########
# Schemas for API query parameters or request body

class BuildingQueryArgsSchema(ma.Schema):
    """Building get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Filter by building name'
    )
    kind = ma.fields.String(
        validate=validate_kind,
        description='Filter by building type'
    )
    site_id = ma.fields.UUID(
        description='Filter by the associated site, using the site UUID.'
    )
    # TODO: should be min_area or max_area.
    # area = ma.fields.Integer(
    #     description='Filter by the total surface of the building'
    # )


class BuildingRequestBodySchema(BuildingSchema):
    """Building post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)


##########
# Schema for API responses

class BuildingHateoasSchema(ma_hateoas.Schema):
    """Building hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links', '_embedded',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='buildings.BuildingsById', building_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='buildings.Buildings'),
        'parent': ma_hateoas.URLFor(
            endpoint='sites.SitesById', site_id='<site_id>'),
        'kinds': ma_hateoas.URLFor(endpoint='buildings.BuildingTypes'),
        # TODO: write this endpoint
        # 'distance_units': ma_hateoas.URLFor(
        #     endpoint='distanceunits.distanceunits'),
    }, description='HATEOAS resource links')

    _embedded = ma_hateoas.Hyperlinks(schema={
        'floors': {
            '_links': {
                'collection': ma_hateoas.URLFor(
                    endpoint='floors.Floors', building_id='<id>')
            }
        },
    }, description='HATEOAS embedded resources links')


@rest_api.definition('Building')
class BuildingSchemaView(BuildingSchema, BuildingHateoasSchema):
    """Building schema for api views, with hateoas"""

    class Meta(BuildingHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = BuildingHateoasSchema.Meta.dump_only + ('id',)


##########
# Schema for API etag feature

class BuildingEtagSchema(BuildingSchema):
    """Building schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
