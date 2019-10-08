"""Api measures module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ....models import (
    Measure, MeasureValueProperties, MeasureMaterialProperties)

from ....database.db_enums import DBEnumHandler


def validate_obs_type(value):
    """Validate a input observation type."""
    dbhandler = DBEnumHandler()
    obs_types = dbhandler.get_observation_types()
    if value not in obs_types.get_names():
        raise ma.ValidationError('Unknown observation type.')


def validate_medium_type(value):
    """Validate a input medium type."""
    dbhandler = DBEnumHandler()
    medium_types = dbhandler.get_medium_types()
    if value not in medium_types.get_names():
        raise ma.ValidationError('Unknown medium type.')


def validate_unit(value):
    """Validate a input unit."""
    dbhandler = DBEnumHandler()
    units = dbhandler.get_units()
    if value not in units.get_names():
        raise ma.ValidationError('Unknown unit.')


###########
# Schemas for API query parameters or request body

class MaterialPropertiesSchema(ObjectSchema):
    """Measure Properties Schema"""

    _OBJ_CLS = MeasureMaterialProperties

    class Meta:
        """Schema Meta properties"""
        strict = True

    latency = ma.fields.Integer(
        description=(
            'The time (in ms) between a request for an observation and the'
            'sensor providing a result'),
        validate=ma.validate.Range(min=0)
    )
    accuracy = ma.fields.Float(
        description=(
            'The closeness of agreement between the value of an'
            'observation and the true value of the observed quality.'),
        validate=ma.validate.Range(min=0, max=1)
    )
    precision = ma.fields.Float(
        description=(
            'The closeness of agreement between replicate observations'
            'on an unchanged or similar quality value: i.e., a measure of a'
            'sensor\'s ability to consitently reproduce an observation.'),
        validate=ma.validate.Range(min=0, max=1)
    )
    sensitivity = ma.fields.Float(
        description=(
            'Sensitivity is the quotient of the change in a result'
            'of sensor and the corresponding change in a value of a quality'
            ' being observed.'),
    )


class ValuePropertiesSchema(ObjectSchema):
    """Measure range schema"""

    _OBJ_CLS = MeasureValueProperties

    class Meta:
        """Schema Meta properties"""
        strict = True

    vmin = ma.fields.Number(
        description='Minimun value accepted by the sensor',
    )

    vmax = ma.fields.Number(
        description='Maximum value accepted by the sensor',
    )
    frequency = ma.fields.Integer(
        description='The frequency of observation capture in ms.',
        validate=ma.validate.Range(min=0)
    )


class LocationSchema(ObjectSchema):
    """Location schema. Simply a pair type, UUID"""

    _OBJ_CLS = MeasureValueProperties

    class Meta:
        """Schema Meta properties"""
        strict = True
    # TODO: should be replaced with the URL of location, at least include it.
    type = ma.fields.String(
        description='''Type of location. Should be Site, Building, Floor,
        Space or Zone''',
    )
    id = ma.fields.UUID(
        description='The unique identifier of this location',
    )


class MeasureSchema(ObjectSchema):
    """Measure schema"""

    _OBJ_CLS = Measure

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        required=True,
        dump_only=True,
        description='Measure ID'
    )
    sensor_id = ma.fields.UUID(
        required=True,
        description=(
            'The unique identifier of the sensor that performs the measure.')
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description=(
            'Description of the measure in an easily and understandable way.')
    )
    unit = ma.fields.String(
        required=True,
        # validate=validate_unit,
        description=(
            '''The unit associated to the measure, as it is sent by the sensor.
            Must belong to the list of units (see the /measures/units API)''')
    )
    observation_type = ma.fields.String(
        validate=validate_obs_type,
        description=(
            '''The type of observation/measure. The returned value must belong
            to the list of obervation type (see the
            /measures/observation_types/ API)''')
    )
    medium = ma.fields.String(
        validate=validate_medium_type,
        description='''The physical medium on which the measure is performed.
            This is to be read in conjunction with the observation type. For
            instance an ambient air temperature sensor would have
            observation_type=Temperature and medium=Air.
            The list of medium_type can be found in the
            /measures/medium_types API.'''
    )
    on_index = ma.fields.Boolean(
        description='''Indicates whether the measure is made on an index. In
            this case, values are cumulative.'''
    )
    set_point = ma.fields.Boolean(
        description='''Indicates whether the measure is a set point.
            False by default'''
    )
    outdoor = ma.fields.Boolean(
        description='''Indicates whether the measure is made outdoor. If True
            the value could be considered as a weather measure - for instance
            if set to True and medium=Air, this indicates an outdoor
            temperature'''
    )
    ambient = ma.fields.Boolean(
        description='''Indicates whether the measure is an ambient one or note.
            For instance, a sensor measurement performed on the temperature in
            some room/area of a building. Set points and measures made on HVAC
            equipment must not be ambient.'''
    )
    external_id = ma.fields.String(
        description='''The external ID for this measure. The ID that must be
            used to access values of the measure'''
    )
    method = ma.fields.String(
        description='''The method used to perform the measure
            (i.e. at a certain frequency or on value change)'''
    )
    material_properties = ma.fields.Nested(
        MaterialPropertiesSchema,
        description='Material Properties that may help understand measurements'
    )
    value_properties = ma.fields.Nested(
        ValuePropertiesSchema,
        description='Properties of this measure'
    )


class MeasureQueryArgsSchema(ma.Schema):
    """Measure get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    observation_type = ma.fields.String(
        validate=validate_obs_type,
        description='Filter by type of observation performed by the sensor'
    )
    medium = ma.fields.String(
        validate=validate_medium_type,
        description='Filter by the physical medium monitored'
    )
    external_id = ma.fields.String(
        description='Filter by external ID'
    )
    outdoor = ma.fields.Boolean(
        description='Filter by outdoor measures'
    )
    location_id = ma.fields.UUID(
        description='Unique Identifier for a site, building, floor or space.'
    )
    on_index = ma.fields.Boolean(
        description='True if filtering on measures on index',
    )
    set_point = ma.fields.Boolean(
        description='True if filtering on set points',
    )
    ambient = ma.fields.Boolean(
        description='True if filtering on ambient measures',
    )


class MeasureRequestBodySchema(MeasureSchema):
    """Measure post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)

    associated_locations = ma.fields.List(
        ma.fields.UUID,
        description='''The list of UUID for the locations of interest for
            this measure.
            Locations of interest are those for which the measure is performed.
            For instance, the room where a sensor measures the temperature, or
            the floor heated by a heating system for which a counter is
            installed.'''
    )
    # device_id = ma.fields.UUID(
    #     description='Unique Identifier for the associated device'
    # )
    # relToSystem = ma.fields.String(
    #     description='Unique Name of a relation'
    # )
    # systemType = ma.fields.String(
    #     description='Unique Name of a system type'
    # )


###########
# Schema for API responses

class MeasureHateoasSchema(ma_hateoas.Schema):
    """Measure hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='measures.MeasureById', measure_id='<id>'),
    }, description='HATEOAS resource links')


@rest_api.definition('Measures')
class MeasureSchemaView(MeasureSchema, MeasureHateoasSchema):
    """Measure values schema for api views. No HATEOAS"""

    class Meta(MeasureHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = MeasureHateoasSchema.Meta.dump_only + ('id',)

    associated_locations = ma.fields.List(
        ma.fields.Nested(LocationSchema),
        description='''The list of locations of interest for this measure.
            Locations of interest are those for which the measure is performed.
            For instance, the room where a sensor measures the temperature, or
            the floor heated by a heating system for which a counter is
            installed.'''
    )


#############
# Schema for API etag feature

class MeasureEtagSchema(MeasureSchema):
    """Measure schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
