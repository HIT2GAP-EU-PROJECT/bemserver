""""Schemas to serialize/deserialize system objects in DB"""

import marshmallow as ma
from marshmallow_oneofschema import OneOfSchema

from .schemas import BaseSchema
from ...models.modules import (
    Service, Model, Output, Parameter, OutputEvent, ValuesDescription,
    OutputTimeSeries)


class _OutputSchema(BaseSchema):
    """Schema to validate sensor's extraction from the ontology"""
    _OBJ_CLS = Output

    id = ma.fields.UUID(
        required=True,
        description='A unique ID for this output',
    )

    module_id = ma.fields.UUID(
        required=True,
        description='Parent service for this output'
    )
    model_id = ma.fields.UUID(
        required=True,
        description='Parent model for this output'
    )


class ParameterSchema(BaseSchema):
    """Schema to serialize Parameters"""

    _OBJ_CLS = Parameter

    name = ma.fields.String(
        required=True,
        description="Parameter's name",
    )
    value = ma.fields.Number(
        required=True,
        description="Parameter's value",
    )


class ServiceSchema(BaseSchema):
    """Schema to validate localization's extraction from the ontology"""
    _OBJ_CLS = Service

    id = ma.fields.UUID(  # pylint: disable=invalid-name
        required=True,
        description='Service ID'
    )
    name = ma.fields.String(
        description='Name of the service - a short name to identify it'
    )
    description = ma.fields.String(
        description='Description of the service.',
    )
    kind = ma.fields.String(
        description='Kind of service',
    )
    url = ma.fields.String(
        description='The URL to call the service',
    )
    has_frontend = ma.fields.Boolean(
        description='''Indicates whether the module has a frontend. If True, the
            url can be used for display purpose within the Hit2Gap portal'''
    )
    site_ids = ma.fields.List(
        ma.fields.UUID(),
        description='''The list of sites on which the module is installed.
            Sites are identified with their UUIDs''',
    )
    model_ids = ma.fields.List(
        ma.fields.UUID(),
    )


class OutputEventSchema(_OutputSchema):
    """Schema to validate MeasureValueProperties"""
    _OBJ_CLS = OutputEvent


class _ValuesDescriptionSchema(BaseSchema):
    """Schema to validate MeasureValueProperties"""
    _OBJ_CLS = ValuesDescription

    kind = ma.fields.String(
        description='The type of values generated',
        required=True,
    )
    unit = ma.fields.String(
        description='The unit for the values generated',
        required=True,
    )
    sampling = ma.fields.Float(
        description='The frequency at which the data are generated',
    )


class OutputTSSchema(_OutputSchema):
    """Schema to validate sensor's extraction from the ontology"""
    _OBJ_CLS = OutputTimeSeries

    localization = ma.fields.UUID(
        required=True,
        description='''The unique ID of the localization related to the data
            generated''',
    )
    values_desc = ma.fields.Nested(
        _ValuesDescriptionSchema,
        required=True,
        description='Description of the values generated'
    )
    external_id = ma.fields.String(
        description='''External ID to store values of the measures on the HDF5
            instance''',
    )


class OutputSchema(OneOfSchema):
    type_field = 'cls'
    type_schemas = {
        'Event': OutputEventSchema,
        'TimeSeries': OutputTSSchema,
    }

    def get_obj_type(self, obj):
        if isinstance(obj, OutputEvent):
            return 'Event'
        elif isinstance(obj, OutputTimeSeries):
            return 'TimeSeries'
        else:
            raise Exception('Unknown object type: %s' % obj.__class__.__name__)


class ModelSchema(BaseSchema):
    """Schema to validate system's extraction from the ontology
    Must not be instantiated by inherited by other schemas"""
    _OBJ_CLS = Model

    id = ma.fields.UUID(  # pylint: disable=invalid-name
        required=True,
        description='Model ID'
    )
    name = ma.fields.String(
        required=True,
        description='Model name'
    )
    description = ma.fields.String(
        description='Model description'
    )
    event_output_ids = ma.fields.List(
        ma.fields.UUID(),
        description='The list of event outputs associated to this model',
    )
    timeseries_output_ids = ma.fields.List(
        ma.fields.UUID(),
        description='The list of timeseries outputs associated to this model',
    )
    service_id = ma.fields.UUID(
        required=True,
        description='The unique ID of the service that uses the current model',
    )
    parameters = ma.fields.List(
        ma.fields.Nested(ParameterSchema),
        description="List of parameters associated to the model",
    )
