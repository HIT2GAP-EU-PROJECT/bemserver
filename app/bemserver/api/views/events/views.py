"""Api events module views"""

from flask.views import MethodView

from bemserver.api.extensions.relational_db import db
from bemserver.api.extensions.rest_api import SQLCursorPage, check_etag
from bemserver.api.extensions.rest_api.doc_responses import (
    build_responses)
from bemserver.api.extensions.auth import (
    auth_required, verify_scope, get_user_account)

from bemserver.models.events import Event

from . import bp as api
from .schemas import EventSchema, EventQueryArgsSchema


@api.route('/')
class Events(MethodView):

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='List events',
        description='''This endpoint allows one to retrieve events by any
service plugged to the BEMServer running instance.

Because the set of generated events can be big, the use of filters is
recommended. Typical filters can be:

+ localization: through the use of site_id, building_id, floor_id.
+ criticity level.
+ category or sub-category.

Also, ensure you correctly use the `page_size` and `page` parameters in your
calls to get the full list of generated events.'''
    )
    @api.arguments(EventQueryArgsSchema, location='query')
    @api.response(EventSchema(many=True))
    @api.paginate(SQLCursorPage)
    def get(self, args):
        """Return event list"""
        sort = args.pop('sort', ())
        sensor_id = args.pop('sensor_id', None)
        min_start_time = args.pop('min_start_time', None)
        max_start_time = args.pop('max_start_time', None)
        min_end_time = args.pop('min_end_time', None)
        max_end_time = args.pop('max_end_time', None)
        items = db.session.query(Event).filter_by(**args)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            items = items.filter(Event.site_id.in_(uacc.sites))
        if sensor_id is not None:
            items = items.filter(
                Event.sensor_ids.contains('"{}"'.format(sensor_id)))
        if min_start_time is not None:
            items = items.filter(Event.start_time >= min_start_time)
        if max_start_time is not None:
            items = items.filter(Event.start_time < max_start_time)
        if min_end_time is not None:
            items = items.filter(Event.end_time >= min_end_time)
        if max_end_time is not None:
            items = items.filter(Event.end_time < max_end_time)
        # TODO: factorize sort logic (in Schema?)
        for name, direc in sort:
            criterion = getattr(
                getattr(Event, name), 'desc' if direc < 0 else 'asc')()
            items = items.order_by(criterion)
        return items

    @auth_required(roles=['module_data_processor'])
    @api.doc(
        summary='Add a new event',
        description='''Endpoint to be called by services when they output some
        event to BEMServer.<br>**Ensure you use the service_id of your service,
        after registering to the `/services` API!**<br>Additionally, the more
        information/fields are set, the easiest it is for other services to
        use the events you generate.''',
        responses=build_responses([201, 422, 500])
    )
    @api.arguments(EventSchema)
    @api.response(EventSchema, code=201)
    def post(self, new_data):
        """Create a new event"""
        item = EventSchema().make_obj(new_data)
        # permissions checks
        verify_scope(sites=[item.site_id])
        db.session.add(item)
        db.session.commit()
        return item


@api.route('/<uuid:event_id>')
class EventsById(MethodView):

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='Get event by ID',
        description='''A specific entrypoint to retrieve events according to the
        the ID associated. Useful for testing purpose to ensure the event is
        stored and available as desired.''',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.response(EventSchema)
    def get(self, event_id):
        """Return an item from its ID"""
        item = db.session.query(Event).get_or_404(event_id)
        # permissions checks
        verify_scope(sites=[item.site_id])
        return item

    @auth_required(roles=['module_data_processor'])
    @api.doc(
        summary='Update existing event',
        description='Update an event from its ID and return updated event.',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.arguments(EventSchema)
    @api.response(EventSchema)
    def put(self, update_data, event_id):
        """Update an item from its ID and return updated item"""
        item = db.session.query(Event).get_or_404(event_id)
        # permissions checks
        verify_scope(sites=[item.site_id])
        check_etag(item, etag_schema=EventSchema)
        EventSchema().update_obj(item, update_data)
        db.session.add(item)
        db.session.commit()
        return item

    @auth_required(roles=['module_data_processor'])
    @api.doc(
        summary='Delete event',
        description='''Delete an event. Requires to have its ID.''',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.response(code=204)
    def delete(self, event_id):
        """Delete an item from its ID"""
        item = db.session.query(Event).get_or_404(event_id)
        # permissions checks
        verify_scope(sites=[item.site_id])
        check_etag(item, etag_schema=EventSchema)
        db.session.delete(item)
        db.session.commit()
