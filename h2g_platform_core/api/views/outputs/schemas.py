"""Api outputs module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.schemas import ObjectSchema

from ....models import OutputEvent, OutputTimeSeries, ValuesDescription


class _OutputSchema(ObjectSchema):
    """Schema to validate sensor's extraction from the ontology"""

    id = ma.fields.UUID(
        dump_only=True,
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


@rest_api.definition('OutputEvent')
class OutputEventSchema(_OutputSchema):
    """Schema to validate MeasureValueProperties"""
    _OBJ_CLS = OutputEvent


# @rest_api.definition('OutputTimeseriesValuesDescription')
class _ValuesDescriptionSchema(ObjectSchema):
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
        description='''The frequency (in seconds) at which the data are
            generated''',
    )


@rest_api.definition('OutputTimeseriesValuesDescription')
class OutputTSSchema(_OutputSchema):
    """Schema to validate sensor's extraction from the ontology"""
    _OBJ_CLS = OutputTimeSeries

    localization = ma.fields.UUID(
        required=True,
        description='''Unique ID of the localization related to the data
            generated''',
    )
    values_desc = ma.fields.Nested(
        _ValuesDescriptionSchema,
        required=True,
        description='Description of generated values'
    )
    external_id = ma.fields.String(
        description='ID of the associated timeseries',
    )


class OutputQueryArgsSchema(ma.Schema):
    """Output get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    module_id = ma.fields.UUID(
        description='Parent service for this output'
    )
    model_id = ma.fields.UUID(
        description='Parent model for this output'
    )
