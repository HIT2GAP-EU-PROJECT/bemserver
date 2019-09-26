"""Api sites module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ..schemas import GeographicInfoSchema, GeographicInfoSchemaView

from ....models import Site


class SiteSchema(ObjectSchema):
    """Site schema"""

    _OBJ_CLS = Site

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        required=True,
        dump_only=True,
        description='The unique identifier (UUID) associated to the site'
    )
    name = ma.fields.String(
        required=True,
        description='A short name associated to the site.'
    )
    geographic_info = ma.fields.Nested(
        GeographicInfoSchema,
        required=True,
        description='Geographical information associated to the site.'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='A description of the site.'
    )


##########
# Schemas for API query parameters or request body

class SiteQueryArgsSchema(ma.Schema):
    """Site get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Used to filter by site name'
    )


class SiteRequestBodySchema(SiteSchema):
    """Site post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)


##########
# Schema for API responses

class SiteHateoasSchema(ma_hateoas.Schema):
    """Site hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links', '_embedded',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='sites.SitesById', site_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='sites.Sites')
    }, description='HATEOAS resource links')

    _embedded = ma_hateoas.Hyperlinks(schema={
        'buildings': {
            '_links': {
                'collection': ma_hateoas.URLFor(
                    endpoint='buildings.Buildings', site_id='<id>')
            }
        },
        # 'distance_units': {
        #     '_links': {
        #         # TODO: write this endpoint
        #         # 'collection': ma_hateoas.URLFor(
        #         #     endpoint='distanceunits.distanceunits')
        #     }
        # },
    }, description='HATEOAS embedded resources links')


@rest_api.definition('Site')
class SiteSchemaView(SiteSchema, SiteHateoasSchema):
    """Site schema for api views, with hateoas"""

    class Meta(SiteHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = SiteHateoasSchema.Meta.dump_only + (
            'id', 'geographic_info.id',)

    geographic_info = ma.fields.Nested(
        GeographicInfoSchemaView,
        required=True,
        description='Site geographical informations'
    )


##########
# Schema for API etag feature

class SiteEtagSchema(SiteSchema):
    """Site schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
