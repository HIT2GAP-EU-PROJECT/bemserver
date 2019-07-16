"""Api occupants module schemas"""

import marshmallow as ma

from ...extensions import marshmallow as ext_ma
from ...extensions.rest_api import rest_api
from ...extensions.rest_api.query import SortQueryArgsSchema
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ....models import (
    Occupant, OccupantWorkSchedule, OccupantWorkspace, OccupantEnergyBehaviour,
    OccupantComfortOperationFrequency, OccupantElectronicUsedQuantity,
    OccupantElectronicUsed,
    AgeCategory,
    WorkspaceType, DistanceToPointType, KnowledgeLevel, ActivityFrequency,
    ComfortType, PreferenceType)

from ....database.db_enums import DBEnumHandler


class OccupantWorkScheduleSchema(ObjectSchema):
    """Occupant work schedule schema"""

    _OBJ_CLS = OccupantWorkSchedule

    class Meta:
        """Schema Meta properties"""
        strict = True

    day = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([
            'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
        description='Occupant\'s work schedule day'
    )
    time_start = ma.fields.Time(
        required=True,
        description='Occupant\'s work schedule start time'
    )
    time_end = ma.fields.Time(
        required=True,
        description='Occupant\'s work schedule end time'
    )


class OccupantWorkspaceSchema(ObjectSchema):
    """Occupant workspace schema"""

    _OBJ_CLS = OccupantWorkspace

    class Meta:
        """Schema Meta properties"""
        strict = True

    kind = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([t.name for t in WorkspaceType]),
        description='Occupant\'s workspace type'
    )
    desk_location_window = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([t.name for t in DistanceToPointType]),
        description='Occupant\'s work desk from window distance type code name'
    )
    desk_location_heater = ma.fields.String(
        validate=ma.validate.OneOf([t.name for t in DistanceToPointType]),
        description='Occupant\'s work desk from HVAC distance type code name'
    )
    desk_location_airconditioner = ma.fields.String(
        validate=ma.validate.OneOf([t.name for t in DistanceToPointType]),
        description='Occupant\'s work desk from HVAC distance type code name'
    )


class OccupantEnergyBehaviourSchema(ObjectSchema):
    """Occupant energy behaviour schema"""

    _OBJ_CLS = OccupantEnergyBehaviour

    class Meta:
        """Schema Meta properties"""
        strict = True

    awareness_level = ma.fields.String(
        validate=ma.validate.OneOf([kl.name for kl in KnowledgeLevel]),
        description='Occupant\'s energy awareness knownledge level code name'
    )
    awareness_activities = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Occupant\'s energy awareness activity frequency code name'
    )


class OccupantComfortOperationFrequencySchema(ObjectSchema):
    """Occupant comfort operation frequency schema"""

    _OBJ_CLS = OccupantComfortOperationFrequency

    class Meta:
        """Schema Meta properties"""
        strict = True

    window_shades = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Window shades operation frequency code name'
    )
    curtains = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Curtains operation frequency code name'
    )
    thermostat = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Thermostat operation frequency code name'
    )
    portable_fan = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Portable fan operation frequency code name'
    )
    ceiling_fan = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Ceiling fan operation frequency code name'
    )
    ceiling_air_ventilation = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Ceiling air ventilation operation frequency code name'
    )
    floor_air_ventilation = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Floor air ventilation operation frequency code name'
    )
    light_switch = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Light switch operation frequency code name'
    )
    light_dimmer = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Light dimmer operation frequency code name'
    )
    desk_light = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Desk light operation frequency code name'
    )
    hvac_unit = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='HVAC unit operation frequency code name'
    )
    other_1 = ma.fields.String(
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Other #1 operation frequency code name'
    )
    other_2 = ma.fields.String(
        validate=ma.validate.OneOf([af.name for af in ActivityFrequency]),
        description='Other #2 operation frequency code name'
    )


class OccupantElectronicUsedQuantitySchema(ObjectSchema):
    """Occupant electronic used quantity schema"""

    _OBJ_CLS = OccupantElectronicUsedQuantity

    class Meta:
        """Schema Meta properties"""
        strict = True

    electronic_kind = ma.fields.String(
        required=True,
        # validate=ma.validate.OneOf([
        #     et.name for et in Occupant.get_all_electronic_types()]),
        description='Occupant\'s electronic used kind code name'
    )
    number = ma.fields.Integer(
        required=True,
        validate=ma.validate.Range(min=1),
        description='Occupant\'s number of electronic used'
    )


class OccupantElectronicUsedSchema(ObjectSchema):
    """Occupant electronic used schema"""

    _OBJ_CLS = OccupantElectronicUsed

    class Meta:
        """Schema Meta properties"""
        strict = True

    electronic_used_in_workspace = ma.fields.List(
        ma.fields.Nested(
            OccupantElectronicUsedQuantitySchema,
            description='Occupant\'s electronic used quantity'
        ),
        description='Occupant\'s electronic used list'
    )

    number_connected_device_at_desk = ma.fields.Integer(
        required=True,
        validate=ma.validate.Range(min=1),
        description='Occupant\'s number of connected devices at desk'
    )


def validate_gender(value):
    """Validate a input kind."""
    dbhandler = DBEnumHandler()
    gender_types = dbhandler.get_gender_types()
    gender_type_names = gender_types.get_son_names(indirect=True)
    if value not in gender_type_names:
        raise ma.ValidationError('Unknown gender type.')


class OccupantSchema(ObjectSchema):
    """Occupant schema"""

    _OBJ_CLS = Occupant

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        dump_only=True,
        required=True,
        description='Occupant ID'
    )

    token_id = ma.fields.String(
        description='Occupant token ID'
    )

    gender = ma.fields.String(
        required=True,
        validate=validate_gender,
        description='Occupant gender type code name'
    )
    age_category = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([ac.name for ac in AgeCategory]),
        description='Occupant age category code name'
    )

    work_schedule = ma.fields.List(
        ma.fields.Nested(
            OccupantWorkScheduleSchema,
            description='Occupant\'s work schedule'
        ),
        description='Occupant\'s work schedule list'
    )

    workspace = ma.fields.Nested(
        OccupantWorkspaceSchema,
        description='Occupant\'s workspace informations'
    )

    energy_behaviour = ma.fields.Nested(
        OccupantEnergyBehaviourSchema,
        description='Occupant\'s energy behaviour informations'
    )

    comfort_operation_frequencies = ma.fields.Nested(
        OccupantComfortOperationFrequencySchema,
        description='Occupant\'s comfort operation frequency informations'
    )

    electronics = ma.fields.Nested(
        OccupantElectronicUsedSchema,
        description='Occupant\'s electronic used informations'
    )


class ComfortPerceptionSchema(ObjectSchema):
    """Comfort Perception schema"""

    aspects = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([ct.name for ct in ComfortType]),
        description='Comfort type code name'
    )

    perception = ma.fields.Integer(
        required=True,
        validate=ma.validate.Range(min=0, max=7),
        description='Comfort perception values'
    )

    satisfaction = ma.fields.Integer(
        required=True,
        validate=ma.validate.Range(min=0, max=5),
        description='Comfort satisfaction values'
    )

    preference = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf([pt.name for pt in PreferenceType]),
        escription='Comfort preference type code name'
    )


class ComfortSchema(ObjectSchema):
    """Comfort schema"""

    description = ma.fields.String()

    time = ext_ma.fields.StrictDateTime()

    perceptions = ma.fields.List(
        ma.fields.Nested(
            ComfortPerceptionSchema,
            description='Comfort Aspect'
        )
    )


###########
# Schemas for API query parameters or request body

class OccupantQueryArgsSchema(SortQueryArgsSchema):
    """Occupant get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    token_id = ma.fields.String(
        description='Occupant token ID'
    )
    gender = ma.fields.String(
        validate=validate_gender,
        description='Occupant gender type code name'
    )
    age_category = ma.fields.String(
        validate=ma.validate.OneOf([ac.name for ac in AgeCategory]),
        description='Occupant age category code name'
    )


class OccupantRequestBodySchema(OccupantSchema):
    """Occupant post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id', 'workspace.id')


###########
# Schema for API responses

class OccupantHateoasSchema(ma_hateoas.Schema):
    """Occupant hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links')

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='occupants.OccupantById', occupancy_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='occupants.Occupants'),
    }, description='HATEOAS resource links')

    _embedded = ma_hateoas.Hyperlinks(schema={
        'gender_types': {
            '_links': {
                'collection': ma_hateoas.URLFor(
                    endpoint='occupants.OccupantGenderType')
            }
        },
        'age_categories': {
            '_links': {
                'collection': ma_hateoas.URLFor(
                    endpoint='occupants.OccupantAgeCategory')
            }
        }
    }, description='HATEOAS embedded resources links')


@rest_api.definition('Occupant')
class OccupantSchemaView(OccupantSchema, OccupantHateoasSchema):
    """Occupant schema for api views, with hateoas"""

    class Meta(OccupantHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = OccupantHateoasSchema.Meta.dump_only + ('workspace.id')


class GenericTypeSchemaView(ma.Schema):
    """Generic types schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('name', 'label',)

    name = ma.fields.String(
        description='Type code name'
    )
    label = ma.fields.String(
        description='Type label (for human reading)'
    )


@rest_api.definition('AgeCategory')
class AgeCategorySchemaView(GenericTypeSchemaView):
    """Age Category schema for api views"""


@rest_api.definition('OccupantWorkspaceType')
class OccupantWorkspaceTypeSchemaView(GenericTypeSchemaView):
    """Occupant Workspace Types schema for api views"""


@rest_api.definition('OccupantDistanceToPointType')
class OccupantDistanceToPointTypeSchemaView(GenericTypeSchemaView):
    """Occupant Distance To Point Types schema for api views"""


@rest_api.definition('OccupantKnowledgeLevel')
class OccupantKnowledgeLevelSchemaView(GenericTypeSchemaView):
    """Occupant Knowledge Levels schema for api views"""


@rest_api.definition('OccupantActivityFrequency')
class OccupantActivityFrequencySchemaView(GenericTypeSchemaView):
    """Occupant Activity Frequency schema for api views"""


@rest_api.definition('OccupantElectronicType')
class OccupantElectronicTypeSchemaView(ma.Schema):
    """Occupant available electronic type schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('name', 'label', 'parent_name',)

    name = ma.fields.String(
        description='Type code name'
    )
    label = ma.fields.String(
        load_from='label_breadcrumb',
        description='Type label (for human reading)'
    )
    parent_name = ma.fields.String(
        description='Parent type code name'
    )


#############
# Schema for API etag feature

class OccupantEtagSchema(OccupantSchema):
    """Occupant schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
