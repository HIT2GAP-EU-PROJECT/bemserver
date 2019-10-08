"""Api services module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.schemas import ObjectSchema

from ....models import Model, Parameter


@rest_api.definition('ModelParameter')
class ParameterSchema(ObjectSchema):
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


@rest_api.definition('Model')
class ModelSchema(ObjectSchema):
    """Model schema"""

    _OBJ_CLS = Model

    id = ma.fields.UUID(
        dump_only=True,
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
        ma.fields.UUID('Output ID'),
        dump_only=True,
        description='The list of event outputs associated to this model',
    )
    timeseries_output_ids = ma.fields.List(
        ma.fields.UUID('Output ID'),
        dump_only=True,
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

    class Meta:
        """Schema Meta properties"""
        strict = True


class ModelQueryArgsSchema(ma.Schema):
    """Model get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    service_id = ma.fields.UUID(
        description='Service ID',
    )
