"""Some common schema views"""

import marshmallow as ma

from ..extensions.rest_api import rest_api
from ..extensions.rest_api.hateoas import ma_hateoas
from ..extensions.rest_api.schemas import ObjectSchema

from ...models import (
    SpatialInfo, OrientedSpatialInfo, SurfaceInfo, GeographicInfo,
    Localization, System)

from ...database.db_enums import DBEnumHandler


@rest_api.definition('Node')
class TreeSchemaView(ma.Schema):
    """Schema of hierarchical types for API views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        ordered = True
        dump_only = ('children', 'label', 'level', 'name', 'parent',
                     'label_breadcrumb',)

    name = ma.fields.String(
        description='Type name'
    )
    label = ma.fields.String(
        description='Type label'
    )
    level = ma.fields.Integer(
        description='Type level'
    )

    children = ma.fields.Nested(
        'self',
        many=True,
        description='Sub-types'
    )

    parent_name = ma.fields.String(
        attribute='parent.name',
        description='Type parent name'
    )

    label_breadcrumb = ma.fields.String(
        description='Type label breadcrumb'
    )


def validate_hemisphere(value):
    """Validate a input kind."""
    dbhandler = DBEnumHandler()
    hemisphere_types = dbhandler.get_hemisphere_types()
    hemisphere_type_names = hemisphere_types.get_son_names(indirect=True)
    if value not in hemisphere_type_names:
        raise ma.ValidationError('Unknown hemisphere type.')


def validate_climate(value):
    """Validate a input kind."""
    dbhandler = DBEnumHandler()
    climate_types = dbhandler.get_climate_types()
    climate_type_names = climate_types.get_son_names(indirect=True)
    if value not in climate_type_names:
        raise ma.ValidationError('Unknown climate type.')


class GeographicInfoSchema(ObjectSchema):
    """Geographical data schema"""

    _OBJ_CLS = GeographicInfo

    latitude = ma.fields.Float(
        required=True,
        validate=ma.validate.Range(min=-90, max=90),
        description='Geolocation\'s latitude value'
    )
    longitude = ma.fields.Float(
        required=True,
        validate=ma.validate.Range(min=-180, max=180),
        description='Geolocation\'s longitude value'
    )
    altitude = ma.fields.Float(
        description='Altitude value'
    )
    hemisphere = ma.fields.String(
        validate=validate_hemisphere,
        description='''Hemisphere type code name. Must be either `Northern` or
            `Southern` (See
            /api-docs/redoc#tag/geographical/paths/~1geographical~1hemispheres~1/get).'''
    )
    climate = ma.fields.String(
        validate=validate_climate,
        description='''Climate type code name. For the full list of potential
            values, see
            /api-docs/redoc#tag/geographical/paths/~1geographical~1climates~1/get'''
    )


@rest_api.definition('GeographicInfo')
class GeographicInfoSchemaView(GeographicInfoSchema):
    """Geographical data schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True


@rest_api.definition('SpatialInfo')
class SpatialInfoSchema(ObjectSchema):
    """Spatial info schema"""

    _OBJ_CLS = SpatialInfo

    class Meta:
        """Schema Meta properties"""
        strict = True

    area = ma.fields.Float(
        description='Area'
    )
    max_height = ma.fields.Float(
        description='Maximum height'
    )
    volume = ma.fields.Float(
        description='Volume of a structural object'
    )


@rest_api.definition('SurfaceInfo')
class SurfaceInfoSchema(ObjectSchema):
    """Surface info schema"""

    _OBJ_CLS = SurfaceInfo

    class Meta:
        """Schema Meta properties"""
        strict = True

    area = ma.fields.Float(
        description='Area'
    )
    max_height = ma.fields.Float(
        description='Maximum height'
    )
    width = ma.fields.Float(
        description='Width of a structural object'
    )


def validate_orientation(value):
    """Validate a input kind."""
    dbhandler = DBEnumHandler()
    orientation_types = dbhandler.get_orientation_types()
    orientation_type_names = orientation_types.get_son_names(indirect=True)
    if value not in orientation_type_names:
        raise ma.ValidationError('Unknown orientation type.')


@rest_api.definition('OrientedSpatialInfo')
class OrientedSpatialInfoSchema(ObjectSchema):
    """Oriented spatial info schema"""

    _OBJ_CLS = OrientedSpatialInfo

    class Meta:
        """Schema Meta properties"""
        strict = True

    area = ma.fields.Float(
        required=True,
        description='Area'
    )
    orientation = ma.fields.String(
        validate=validate_orientation,
        missing='North',
        description='Orientation'
    )


class LocalizationSchema(ObjectSchema):
    """DeviceLocation Marshmallow schema"""

    _OBJ_CLS = Localization

    site_id = ma.fields.UUID(
        description='Unique identifier of a site',
    )
    building_id = ma.fields.UUID(
        description='Unique identifier of a building',
    )
    floor_id = ma.fields.UUID(
        description='Unique identifier of a floor',
    )
    space_id = ma.fields.UUID(
        description='Unique identifier of a space',
    )


class SystemSchema(ObjectSchema):

    _OBJ_CLS = System

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        required=True,
        dump_only=True,
        description='System ID'
    )
    name = ma.fields.String(
        required=True,
        description='System name'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='System description'
    )
    localization = ma.fields.Nested(
        LocalizationSchema,
        description='Localization of the system'
    )


class SystemQueryArgsSchema(ma.Schema):
    """System get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    name = ma.fields.String(
        description='System name'
    )
    site_id = ma.fields.UUID(
        description=(
            'The unique identifier of the site in which the device is located')
    )
    building_id = ma.fields.UUID(
        description=(
            'The unique identifier of the building in which device is located')
    )
    floor_id = ma.fields.UUID(
        description=(
            'The unique identifier of the floor in which device is located')
    )
    space_id = ma.fields.UUID(
        description=(
            'The unique identifier of the space in which device is located')
    )


class SystemRequestBodySchema(SystemSchema):
    """System post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)


class SystemHateoasSchema(ma_hateoas.Schema):
    """System HATEOAS part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links', '_embedded',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='systems.systembyid', device_id='<id>'),
        # 'site': ma_hateoas.URLFor(
        #     endpoint='sites.sitebyid', site_id='<site_id>')
        # TODO: create endpoint devices.devicetypes
        # 'kind': ma_hateoas.URLFor(endpoint='devices.devicetypes'),
        # TODO: create endpoints or URLs at least
        # 'systems': ma.fields.Nested(_RelationToSystem),
        # 'energy': ma.fields.Nested(_RelationToEnergy),
        # 'measures': ma.fields.List(
        #     ma_hateoas.URLFor(
        #         endpoint='measures.measurebyid', device_id='<id>')
        # )

        # TODO: write this endpoint
        # 'distance_units': ma_hateoas.URLFor(
        #     endpoint='distanceunits.distanceunits'),
    }, description='HATEOAS resource links')


@rest_api.definition('System')
class SystemSchemaView(SystemSchema, SystemHateoasSchema):
    """System schema for api views, with hateoas"""

    class Meta(SystemHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = SystemHateoasSchema.Meta.dump_only + ('id',)
