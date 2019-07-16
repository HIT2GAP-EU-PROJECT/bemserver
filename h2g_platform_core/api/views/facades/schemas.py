"""Api facades module schemas"""

# pylint: disable=too-few-public-methods

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ..schemas import SurfaceInfoSchema

from ....models.facade import Facade


class FacadeSchema(ObjectSchema):
    """Facade schema"""

    _OBJ_CLS = Facade

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(  # pylint: disable=invalid-name
        required=True,
        dump_only=True,
        description='Facade ID'
    )
    name = ma.fields.String(
        required=True,
        description='Facade name'
    )
    spaces = ma.fields.List(
        ma.fields.UUID(
            required=True,
            description='A space ID',
        ),
        required=True,
        description='A list of spaces ID related to the facade',
    )
    surface_info = ma.fields.Nested(
        SurfaceInfoSchema,
        description='Facade spatial informations'
    )
    orientation = ma.fields.String(
        description='Orientation of the facade'
    )
    windows_wall_ratio = ma.fields.Float(
        validate=ma.validate.Range(min=0, max=1),
        description='Windows wall ratio'
    )
    building_id = ma.fields.UUID(
        required=True,
        description='Facade\'s building ID'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Facade description'
    )


##########
#  Schemas for API query parameters or request body

class FacadeQueryArgsSchema(ma.Schema):
    """Facade get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='Facade name'
    )
    building_id = ma.fields.UUID(
        description='Facade\'s building ID'
    )


class FacadeRequestBodySchema(FacadeSchema):
    """Facade post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id', 'surface_info.id',)


##########
# Schema for API responses

class FacadeHateoasSchema(ma_hateoas.Schema):
    """Facade hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links', '_embedded',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='facades.FacadesById', facade_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='facades.Facades'),
        'parent': ma_hateoas.URLFor(
            endpoint='buildings.BuildingsById', building_id='<building_id>'),
        #  TODO: write this endpoint
        # 'distance_units': ma_hateoas.URLFor(
        #     endpoint='distanceunits.distanceunits'),
    }, description='HATEOAS resource links')

    _embedded = ma_hateoas.Hyperlinks(schema={
        'windows': {
            '_links': {
                #  TODO: just do it !
                # 'collection': ma_hateoas.URLFor(
                #     endpoint='windows.Windows', floor_id='<id>')
            }
        },
    }, description='HATEOAS embedded resources links')


@rest_api.definition('Facade')
class FacadeSchemaView(FacadeSchema, FacadeHateoasSchema):
    """Facade schema for api views, with hateoas"""

    class Meta(FacadeHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = FacadeHateoasSchema.Meta.dump_only + ('id',)


##########
# Schema for API etag feature

class FacadeEtagSchema(FacadeSchema):
    """Facade schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
