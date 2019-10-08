"""Schemas to serialize/deserialize objects in DB"""

import marshmallow as ma

from ...models.geography import GeographicInfo
from ...models.spatial import SpatialInfo, SurfaceInfo
from ...models.quantity import Quantity
from ...models.site import Site
from ...models.building import Building
from ...models.floor import Floor
from ...models.space import Space, SpaceOccupancy
from ...models.zone import Zone
from ...models.facade import Facade
from ...models.slab import Slab
from ...models.window import Window


# TODO: review/remove validators (required, ranges,...)?


class BaseSchema(ma.Schema):
    """Base Schema class"""

    # Class corresponding to the Schema in the data model
    # Override this in children classes
    _OBJ_CLS = None

    @ma.pre_load
    def remove_none(self, data):
        """Remove keys where value is None"""
        return {k: v for k, v in data.items() if v is not None}

    @ma.post_load
    def make_object(self, data):
        """Instantiate object with deserialized data"""
        return self._OBJ_CLS(**data)

    class Meta:
        """Schema Meta properties"""
        strict = True


class QuantitySchema(BaseSchema):
    """Quantity schema"""

    _OBJ_CLS = Quantity

    kind = ma.fields.String()
    value = ma.fields.Float()
    unit = ma.fields.String()


class GeographicInfoSchema(BaseSchema):
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
        # validate=validate_hemisphere,
        description='Hemisphere type code name'
    )
    climate = ma.fields.String(
        # validate=validate_climate,
        description='Climate type code name'
    )


class SpatialInfoSchema(BaseSchema):
    """Volume spatial info schema"""

    _OBJ_CLS = SpatialInfo

    area = ma.fields.Float(
        description='Area'
    )
    max_height = ma.fields.Float(
        description='Maximum height'
    )
    volume = ma.fields.Float(
        description='Volume of a spatial element'
    )


class SiteSchema(BaseSchema):
    """Site schema"""

    _OBJ_CLS = Site

    id = ma.fields.UUID(
        required=True,
        description='Site ID'
    )
    name = ma.fields.String(
        required=True,
        description='Site name'
    )
    distance_unit = ma.fields.String(
        # validate=ma.validate.OneOf([u.name for u in MeasureUnitSpatial]),
        # missing=MeasureUnitSpatial.get_default_name(),
        description='Site distance unit system code name'
    )
    geographic_info = ma.fields.Nested(
        GeographicInfoSchema,
        required=True,
        description='Site geographical informations'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Site description'
    )


class BuildingSchema(BaseSchema):
    """Building schema"""

    _OBJ_CLS = Building

    id = ma.fields.UUID(
        required=True,
        description='Building ID'
    )
    name = ma.fields.String(
        required=True,
        description='Building name'
    )
    kind = ma.fields.String(
        required=True,
        # validate=validate_kind,
        description='Building type code name'
    )
    area = ma.fields.Float(
        validate=ma.validate.Range(min=0),
        description='Building area'
    )
    site_id = ma.fields.UUID(
        required=True,
        description='Building\'s site ID'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Building description'
    )


class FloorSchema(BaseSchema):
    """Floor schema"""

    _OBJ_CLS = Floor

    id = ma.fields.UUID(
        required=True,
        description='Floor ID'
    )
    name = ma.fields.String(
        required=True,
        description='Floor name'
    )
    kind = ma.fields.String(
        required=True,
        # validate=validate_kind,
        description='Floor type code name'
    )
    level = ma.fields.Integer(
        description='Floor level number'
    )
    spatial_info = ma.fields.Nested(
        SpatialInfoSchema,
        # required=True,
        description='Floor spatial informations'
    )
    building_id = ma.fields.UUID(
        required=True,
        description='Floor\'s building ID'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Floor description'
    )


class SpaceOccupancySchema(BaseSchema):
    """Occupancy description of a space"""

    _OBJ_CLS = SpaceOccupancy

    nb_permanents = ma.fields.Integer(
        validate=ma.validate.Range(min=0),
        description='Space occupancy: number of permanents'
    )
    nb_max = ma.fields.Integer(
        validate=ma.validate.Range(min=0),
        description='Space occupancy: maximum number of occupants'
    )


class SpaceSchema(BaseSchema):
    """Space schema"""

    _OBJ_CLS = Space

    id = ma.fields.UUID(
        required=True,
        description='Space ID'
    )
    name = ma.fields.String(
        required=True,
        description='Space name'
    )
    kind = ma.fields.String(
        required=True,
        # validate=validate_kind,
        description='Space type code name'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Space description'
    )
    occupancy = ma.fields.Nested(
        SpaceOccupancySchema,
        # required=True,
        default=None,
        description='Space occupancy informations'
    )
    spatial_info = ma.fields.Nested(
        SpatialInfoSchema,
        # required=True,
        description='Space spatial informations'
    )
    # distance_unit = ma.fields.String(
    #     # validate=ma.validate.OneOf([u.name for u in MeasureUnitSpatial]),
    #     # missing=MeasureUnitSpatial.get_default_name(),
    #     description='Space distance unit system'
    # )
    floor_id = ma.fields.UUID(
        required=True,
        description='Space floor ID'
    )


class ZoneSchema(BaseSchema):
    """Zone description, as a building part"""

    _OBJ_CLS = Zone

    id = ma.fields.UUID(
        required=True,
        description='Zone ID'
    )
    name = ma.fields.String(
        required=True,
        description='Zone name'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Zone description'
    )
    zones = ma.fields.List(
        ma.fields.UUID(
            description='A zone ID',
        ),
        missing=[],
        description='A list of zones ID defining the zone',
    )
    spaces = ma.fields.List(
        ma.fields.UUID(
            description='A space ID',
        ),
        missing=[],
        description='A list of spaces ID defining the zone',
    )
    building_id = ma.fields.UUID(
        description='Zone\'s building ID'
    )


class SurfaceInfoSchema(BaseSchema):
    """Surface spatial info schema"""

    _OBJ_CLS = SurfaceInfo

    area = ma.fields.Float(
        description='Area'
    )
    max_height = ma.fields.Float(
        description='Maximum height'
    )
    width = ma.fields.Float(
        description='width'
    )


class FacadeSchema(BaseSchema):
    """Zone description, as a building part"""

    _OBJ_CLS = Facade

    id = ma.fields.UUID(
        required=True,
        description='Facade ID'
    )
    name = ma.fields.String(
        required=True,
        description='Facade name'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Facade description'
    )
    windows_wall_ratio = ma.fields.Float(
        allow_none=True,
        validate=ma.validate.Range(min=0, max=1),
        description='The ratio of surface occupied by windows on the wall'
    )
    interior = ma.fields.Boolean(
        description='True if the wall is part of the external envelope'
    )
    windows = ma.fields.List(
        ma.fields.UUID(
            description='A window ID',
        ),
        missing=[],
        description='A list of windows ID in the wall described',
    )
    spaces = ma.fields.List(
        ma.fields.UUID(
            description='A spatial structural element ID',
        ),
        missing=[],
        description='''A list of spatial structural element ID defining the
            zone''',
    )
    building_id = ma.fields.UUID(
        description='Facade\'s building ID'
    )
    surface_info = ma.fields.Nested(
        SurfaceInfoSchema,
        description='Information relative to the surface of the wall'
    )
    orientation = ma.fields.String(
        description='Orientation of the façade'
    )


class SlabSchema(BaseSchema):
    """Zone description, as a building part"""

    _OBJ_CLS = Slab

    id = ma.fields.UUID(
        required=True,
        description='Facade ID'
    )
    name = ma.fields.String(
        required=True,
        description='Facade name'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Facade description'
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
        description='Facade\'s building ID'
    )
    surface_info = ma.fields.Nested(
        SurfaceInfoSchema,
        description='Information relative to the surface of the wall'
    )
    kind = ma.fields.String(
        description='The kind of slab',
        required=True,
    )


class WindowSchema(BaseSchema):
    """Window description, as a building part"""

    _OBJ_CLS = Window

    id = ma.fields.UUID(
        required=True,
        description='Window ID'
    )
    name = ma.fields.String(
        required=True,
        description='Window name'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Window description'
    )
    facade_id = ma.fields.UUID(
        required=True,
        description='Facade\'s ID on which the window is'
    )
    surface_info = ma.fields.Nested(
        SurfaceInfoSchema,
        description='Information relative to the surface of the wall'
    )
    orientation = ma.fields.String(
        description='Orientation of the window'
    )
    covering = ma.fields.String(
        description='The type of covering for this window'
    )
    glazing = ma.fields.String(
        description='Type of glazing - single, double'
    )
    u_value = ma.fields.Float(
        description='''The U-value of the window. Indicates thermal
            transmittance'''
    )
