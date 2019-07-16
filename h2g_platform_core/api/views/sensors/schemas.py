"""Api sensors module schemas"""

import marshmallow as ma
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api import rest_api

from ....models import Sensor

from ..schemas import SystemSchema, SystemQueryArgsSchema


###########
# Schemas for API query parameters or request body

class SensorSchema(SystemSchema):
    """Measure schema"""

    _OBJ_CLS = Sensor

    class Meta:
        """Schema Meta properties"""
        strict = True

    static = ma.fields.Boolean(
        description='''True if the sensor is static; otherwise, it is considered
            as a mobile sensor, i.e. localization is not required'''
    )
    system_id = ma.fields.UUID(
        description='The unique identifier of a system attached to the sensor',
    )
    measures = ma.fields.List(
        ma.fields.UUID,
        description='''The unique identifiers to access a description of the
            measures performed by the sensor''',
        dump_only=True,
    )


class SensorQueryArgsSchema(SystemQueryArgsSchema):
    """Sensor get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    static = ma.fields.Boolean(
        description='True (resp False) if sensors must be static (resp mobile)'
    )
    system_id = ma.fields.UUID(
        description='''The unique identifier of a system that must be related to
            the sensors'''
    )
    system_type = ma.fields.String(
        description='''Type of systems that must be related to the sensors'''
    )


class SensorRequestBodySchema(SensorSchema):
    """Sensor post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)


###########
# Schema for API responses

class SensorHateoasSchema(ma_hateoas.Schema):
    """System HATEOAS part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='sensors.SensorById', sensor_id='<id>'),
    }, description='HATEOAS resource links')


@rest_api.definition('Sensors')
class SensorSchemaView(SensorSchema, SensorHateoasSchema):
    """Sensor values schema for api views. No HATEOAS"""

    class Meta(SensorHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = SensorHateoasSchema.Meta.dump_only + ('id',)


#############
# Schema for API etag feature

class SensorEtagSchema(SensorSchema):
    """Sensor schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
