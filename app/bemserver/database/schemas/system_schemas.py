""""Schemas to serialize/deserialize system objects in DB"""

import marshmallow as ma

from .schemas import BaseSchema
from ...models.system import Localization, System
from ...models.monitoring import (
    Sensor, Measure, MeasureMaterialProperties, MeasureValueProperties,
    Location)


class LocalizationSchema(BaseSchema):
    """Schema to validate localization's extraction from the ontology"""
    _OBJ_CLS = Localization

    site_id = ma.fields.UUID(
        description='Site identifier'
    )
    building_id = ma.fields.UUID(
        description='Building identifier',
    )
    floor_id = ma.fields.UUID(
        description='Floor identifier',
    )
    space_id = ma.fields.UUID(
        description='Space identifier',
    )


class SystemSchema(BaseSchema):
    """Schema to validate system's extraction from the ontology
    Must not be instantiated by inherited by other schemas"""
    _OBJ_CLS = System

    id = ma.fields.UUID(
        required=True,
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
        required=True,
        description='Localization of the system'
    )


class SensorSchema(SystemSchema):
    """Schema to validate sensor's extraction from the ontology"""
    _OBJ_CLS = Sensor

    static = ma.fields.Boolean(
        required=True,
        description='Indicates whether the sensor is a mible device or not'
    )
    system = ma.fields.UUID(
        description='Identifer of the system monitored by the sensor'
    )
    measures = ma.fields.List(
        ma.fields.UUID(
            description='A measure ID',
        ),
        missing=[],
        description='A list of measures ID associated to the sensor',
    )


class MeasureValuePropertiesSchema(BaseSchema):
    """Schema to validate MeasureValueProperties"""
    _OBJ_CLS = MeasureValueProperties

    vmax = ma.fields.Float(
        description='The maximal value for the measure',
    )
    vmin = ma.fields.Float(
        description='The minimal value for the measure',
    )
    frequency = ma.fields.Integer(
        description='The frequency of observation capture in ms.',
        validate=ma.validate.Range(min=0)
    )


class MeasureMaterialPropertiesSchema(BaseSchema):
    """Schema to validate MeasureValueProperties"""
    _OBJ_CLS = MeasureMaterialProperties

    latency = ma.fields.Integer(
        description='''The time (in ms) between a request for an observation and the
            sensor providing a result''',
        validate=ma.validate.Range(min=0)
    )
    accuracy = ma.fields.Float(
        description='''The closeness of agreement between the value of an
            observation and the true value of the observed quality.''',
        validate=ma.validate.Range(min=0, max=1)
    )
    precision = ma.fields.Float(
        description='''The closeness of agreement between replicate observations
            on an unchanged or similar quality value: i.e., a measure of a
            sensor's ability to consitently reproduce an observation.''',
        validate=ma.validate.Range(min=0, max=1)
    )
    sensitivity = ma.fields.Float(
        description='''Sensitivity is the quotient of the change in a result of
            sensor and the corresponding change in a value of a quality being
            observed.''',
    )


class MeasureLocationSchema(BaseSchema):
    """Schema to validate location on measures"""
    _OBJ_CLS = Location

    id = ma.fields.UUID(
        description='Unique Identifier of the location element',
        required=True,
    )
    type = ma.fields.String(
        description='Type of location',
        required=True,
    )


class MeasureSchema(BaseSchema):
    """Schema to validate sensor's extraction from the ontology"""
    _OBJ_CLS = Measure

    id = ma.fields.UUID(
        required=True,
        description='Measure ID'
    )
    sensor_id = ma.fields.UUID(
        required=True,
        description=(
            'The unique ID of the sensor that performs the observation'),
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='Window description'
    )
    medium = ma.fields.String(
        description=(
            'The physical medium that is observed (Air, Water, Gaz...)'),
    )
    observation_type = ma.fields.String(
        description=(
            'The physical property that is observed (Temperature, Speed...)'),
    )
    unit = ma.fields.String(
        description='The unit used in this observation',
    )
    value_properties = ma.fields.Nested(
        MeasureValuePropertiesSchema,
        description='The material properties associated to the measure',
    )
    material_properties = ma.fields.Nested(
        MeasureMaterialPropertiesSchema,
        description='The material properties associated to the measure',
    )
    external_id = ma.fields.String(
        description='''External ID to store values of the measures on the
            HDF5 instance''',
    )
    method = ma.fields.String(
        description="""Method for observation capture. Can be of two types: on
        a certain frequency (Frequency) or on value change (OnChange)""",
    )
    associated_locations = ma.fields.List(
        ma.fields.Nested(MeasureLocationSchema),
        description='''Locations of interest for this measures. For instance,
            a consumption measure might be performed by a meter located in a
            specific room of a building, but may measure the overall
            consumption''',
    )
    on_index = ma.fields.Boolean(
        description='''Indicates if the measure is made on an index or not.
            Measures on index are cumulative''',
    )
    set_point = ma.fields.Boolean(
        description='''Indicates if the measure is a set point''',
    )
    outdoor = ma.fields.Boolean(
        description='''Indicates if the measure is performed inside (False) or
            outside of the building (True)  ''',
    )
    ambient = ma.fields.Boolean(
        description='''Indicates if the measure is made on ambiance.''',
    )
