"""Api comforts module schemas"""

import marshmallow as ma

from ...extensions import marshmallow as ext_ma
from ...extensions.rest_api import rest_api
from ...extensions.rest_api.query import SortQueryArgsSchema
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.schemas import ObjectSchema

from ....models import ComfortType, ComfortPerception, Comfort, PreferenceType


###########
# Schemas for API query parameters or request body

class ComfortPerceptionSchema(ObjectSchema):
    """Comfort Perception class"""

    _OBJ_CLS = ComfortPerception

    class Meta:
        """Schema Meta properties"""
        strict = True

    aspect_type = ma.fields.String(
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
        description='Comfort preference type code name'
    )


class ComfortSchema(ObjectSchema):
    """Comfort class"""

    _OBJ_CLS = Comfort

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(  # pylint: disable=invalid-name
        required=True,
        dump_only=True,
        description='Building ID'
    )

    occupant_id = ma.fields.UUID(
        required=True,
        description='The occupant ID related to the comfort information'
    )

    description = ma.fields.String(
        description='Description comfort code name'
    )

    time = ext_ma.fields.StrictDateTime(
        required=True,
        description='Comfort time name'
    )

    perceptions = ma.fields.Nested(
        ComfortPerceptionSchema,
        missing=list,
        many=True,
        description='Comfort Aspect'
    )


class ComfortQueryArgsSchema(SortQueryArgsSchema):
    """Comfort get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True


class ComfortRequestBodySchema(ComfortSchema):
    """Comfort post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id', 'occupant_id,')


###########
# Schema for API responses

class ComfortHateoasSchema(ma_hateoas.Schema):
    """Comfort hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links')

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(
            endpoint='comforts.ComfortById', comfort_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='occupants.Occupants'),
        'parent': ma_hateoas.URLFor(endpoint='zones.Zones'),

    }, description='HATEOAS resource links')

    _embedded = ma_hateoas.Hyperlinks(schema={
        'occupant': {
            '_links': {
                'collection': ma_hateoas.URLFor(
                    endpoint='occupants.Occupants')
            }
        },
        'zone': {
            '_links': {
                'collection': ma_hateoas.URLFor(
                    endpoint='zones.Zones')
            }
        }
    }, description='HATEOAS embedded resources links')


@rest_api.definition('Comfort')
class ComfortSchemaView(ComfortSchema, ComfortHateoasSchema):
    """Occupant schema for api views, with hateoas"""

    class Meta(ComfortHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = ComfortHateoasSchema.Meta.dump_only + ('id')


@rest_api.definition('PreferenceType')
class PreferenceTypeSchemaView(ma.Schema):
    """Preference type schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('name', 'label', 'parent_name', 'level',)

    name = ma.fields.String(
        description='Type code name'
    )
    label = ma.fields.String(
        # load_from='label_breadcrumb',
        description='Type label (for human reading)'
    )
    parent_name = ma.fields.String(
        description='Parent type code name'
    )
    level = ma.fields.Integer(
        description='Type level'
    )


@rest_api.definition('ComfortType')
class ComfortTypeSchemaView(ma.Schema):
    """Comfort type schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('name', 'label', 'parent_name', 'level',)

    name = ma.fields.String(
        description='Type code name'
    )
    label = ma.fields.String(
        # load_from='label_breadcrumb',
        description='Type label (for human reading)'
    )
    parent_name = ma.fields.String(
        description='Parent type code name'
    )
    level = ma.fields.Integer(
        description='Type level'
    )


#############
# Schema for API etag feature

class ComfortEtagSchema(ComfortSchema):
    """Comfort schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
