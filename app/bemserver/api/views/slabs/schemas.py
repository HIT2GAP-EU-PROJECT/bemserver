"""Api slabs module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ..schemas import SurfaceInfoSchema

from ....models.slab import Slab
from ....database.db_enums import DBEnumHandler


def validate_kind(value):
    """Validate an input kind."""
    dbhandler = DBEnumHandler()
    slab_types = dbhandler.get_slab_types()
    slab_type_names = slab_types.get_names()
    if value not in slab_type_names:
        raise ma.ValidationError('Unknown space type.')


class SlabSchema(ObjectSchema):
    """Zone description, as a building part"""

    _OBJ_CLS = Slab

    id = ma.fields.UUID(
        required=True,
        description='Slab ID'
    )
    name = ma.fields.String(
        required=True,
        description='Slab name'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Slab description'
    )
    windows = ma.fields.List(
        ma.fields.UUID(
            description='A window ID',
        ),
        missing=[],
        description='A list of windows ID in the wall described',
    )
    floors = ma.fields.List(
        ma.fields.UUID(
            description='A floor IF',
        ),
        missing=[],
        description='''A list of floors ID delimited by the slab''',
    )
    building_id = ma.fields.UUID(
        description='Slab\'s building ID'
    )
    surface_info = ma.fields.Nested(
        SurfaceInfoSchema,
        description='Information relative to the surface of the wall'
    )
    kind = ma.fields.String(
        validate=validate_kind,
        description='The kind of slab',
    )


##########
#  Schemas for API query parameters or request body

class SlabQueryArgsSchema(ma.Schema):
    """Slab get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Slab name'
    )
    building_id = ma.fields.UUID(
        description='Slab\'s building ID'
    )


class SlabRequestBodySchema(SlabSchema):
    """Slab post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id', 'surface_info.id',)


##########
# Schema for API responses

class SlabHateoasSchema(ma_hateoas.Schema):
    """Slab hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links', '_embedded',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='slabs.SlabsById', slab_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='slabs.Slabs'),
        'parent': ma_hateoas.URLFor(
            endpoint='buildings.BuildingsById', building_id='<building_id>'),
        # TODO: write this endpoint
        # 'distance_units': ma_hateoas.URLFor(
        #     endpoint='distanceunits.distanceunits'),
    }, description='HATEOAS resource links')

    _embedded = ma_hateoas.Hyperlinks(schema={
        'windows': {
            '_links': {
                # TODO: just do it !
                # 'collection': ma_hateoas.URLFor(
                #     endpoint='windows.Windows', floor_id='<id>')
            }
        },
    }, description='HATEOAS embedded resources links')


@rest_api.definition('Slab')
class SlabSchemaView(SlabSchema, SlabHateoasSchema):
    """Slab schema for api views, with hateoas"""

    class Meta(SlabHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = SlabHateoasSchema.Meta.dump_only + ('id',)


##########
# Schema for API etag feature

class SlabEtagSchema(SlabSchema):
    """Slab schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
