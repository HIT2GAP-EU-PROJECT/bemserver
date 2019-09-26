"""Api events module schemas"""

import marshmallow as ma

from bemserver.api.extensions.marshmallow.fields import StringList
from bemserver.api.extensions.rest_api import rest_api
from bemserver.api.extensions.rest_api.query import SortQueryArgsSchema
from bemserver.api.extensions.rest_api.schemas import ObjectSchema

from bemserver.models.events import Event, EventCategory, LEVEL_TYPES


@rest_api.definition('Event')
class EventSchema(ObjectSchema):
    """Event schema"""

    _OBJ_CLS = Event

    class Meta:
        strict = True
        ordered = True

    id = ma.fields.UUID(
        dump_only=True,
        description='Event ID. A unique identifier for the event.'
    )

    application = ma.fields.String(
        required=True,
        validate=ma.validate.Length(max=80),
        description='''UUID of the service/application that generated the event.
            This must refer to an existing ID in the `/services` API.''',
        example='My FDD module'
    )
    model = ma.fields.String(
        validate=ma.validate.Length(max=80),
        description='''Model used to generate the event (an application can run
            on different models). This must refer to an existing ID in the
            `/models` API.''',
        example='Ouf-of-range detection',
    )

    execution_timestamp = ma.fields.DateTime(
        required=True,
        description='The datetime at which the event was generated.'
    )

    site_id = ma.fields.String(
        required=True,
        description='''The unique ID of the site; must be one of the `id` in
            `/sites` API.'''
    )
    building_id = ma.fields.String(
        description='''The unique ID of the building; must be one of the `id` in
            `/buildings` API.'''
    )
    floor_id = ma.fields.String(
        description='''The unique ID of the floor; must be one of the `id` in
            `/floors` API.'''
    )
    space_id = ma.fields.String(
        description='''The unique ID of the space; must be one of the `id` in
            `/spaces` API.'''
    )
    sensor_ids = StringList(
        missing=list,
        description='''A list of sensors, that originated the generation of the
            event. This can be refer to faulty sensors  (`measures` category);
            or the reason why an abnormal consumption was detected...
            <br>The sensor_ids must be taken from the `id` field in the
            `/sensors` API'''
    )

    level = ma.fields.String(
        required=True,
        description='Criticity level (see documentation)',
        validate=ma.validate.OneOf(LEVEL_TYPES),
    )
    category = ma.fields.String(
        required=True,
        description='Category (see documentation)',
        validate=ma.validate.OneOf([c.name for c in EventCategory])
    )

    start_time = ma.fields.DateTime(
        example='2017-01-01T00:00:00',
        description='''The datetime at which the event started. For instance,
        the datetime at which an error on a sensor was detected.'''
    )
    end_time = ma.fields.DateTime(
        example='2017-01-01T00:00:00',
        description='''The datetime at which the event ended (optional).'''
    )

    reliability = ma.fields.Float(
        validate=ma.validate.Range(min=0, max=1),
        description='Reliability of the event. 1 means "100% positive"',
        example=1
    )

    description = ma.fields.String(
        validate=ma.validate.Length(max=400),
        description='''Description of the event. This can be used to add some
            human readable information that can then be displayed to end-users
            by a display service that consumes services; it can also be used to
            add some non-readable information, pre-formatted, that can be
            computed by another service.'''
    )

    @ma.validates_schema
    def _validate_dates(self, data):
        if ('start_time' in data and 'end_time' in data and
                data['start_time'] > data['end_time']):
            raise ma.ValidationError(
                'end_time must be subsequent to start_time')


class EventQueryArgsSchema(SortQueryArgsSchema):
    """Building get query parameters schema"""

    class Meta:
        strict = True
        ordered = True

    site_id = ma.fields.String(
        description='''The unique ID of the site; must be one of the `id` in
            `/sites` API.'''
    )
    building_id = ma.fields.String(
        description='''The unique ID of the building; must be one of the `id` in
            `/buildings` API.'''
    )
    floor_id = ma.fields.String(
        description='''The unique ID of the floor; must be one of the `id` in
            `/floors` API.'''
    )
    sensor_id = ma.fields.String(
        description='''The unique ID of the sensor; must be one of the `id` in
            `/sensors` API.'''
    )

    level = ma.fields.String(
        validate=ma.validate.OneOf(LEVEL_TYPES),
        description='''Allow you to filter by criticity level'''
    )
    category = ma.fields.String(
        validate=ma.validate.OneOf([c.name for c in EventCategory]),
        description='''Allow you to filter by category'''
    )

    min_start_time = ma.fields.DateTime(
        description="""Events for which start_time >= min_start_time will be
            filtered in.""",
        example='2017-01-01T00:00:00')
    max_start_time = ma.fields.DateTime(
        description="""Events for which start_time < max_start_time will be
            filterd in.""",
        example='2017-01-01T00:00:00')
    min_end_time = ma.fields.DateTime(
        description="""Events for which end_time >= end_start_time will be
            filtered in.""",
        example='2017-01-01T00:00:00')
    max_end_time = ma.fields.DateTime(
        description="""Events for which end_time < end_start_time will be
            filtered in.""",
        example='2017-01-01T00:00:00')
