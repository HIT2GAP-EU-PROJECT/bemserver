"""Api outputs module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    OutputEventSchema, OutputTSSchema, OutputQueryArgsSchema)

from ...extensions.rest_api import Page, check_etag, abort
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required

from ....models import Output, OutputEvent, OutputTimeSeries


@api.route('/events/')
class OutputEvents(MethodView):
    """OutputEvent resources endpoint"""

    @auth_required(with_perm=False)
    @api.doc(summary='List event outputs')
    @api.arguments(OutputQueryArgsSchema, location='query')
    @api.response(OutputEventSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return event output list"""
        # XXX: We're reaching a dangerous level of ugliness.
        args['kind'] = 'http://bemserver.org/services#Event'
        return db_accessor.get_list(Output, args)

    @auth_required(
        roles=['chuck', 'module_data_provider', 'module_data_processor'],
        with_perm=False)
    @api.doc(summary='Add a new event output')
    @api.arguments(OutputEventSchema)
    @api.response(OutputEventSchema, code=201)
    def post(self, new_data):
        """Create a new event output"""
        # Save and return new item
        item = OutputEventSchema().make_obj(new_data)
        db_accessor.create(item)
        return item


@api.route('/events/<uuid:output_id>')
class OutputEventsById(MethodView):
    """OutputEvent resource endpoint"""

    def _get_item(self, output_id):
        """Get an item from its ID"""
        ret = db_accessor.get_item_by_id(Output, output_id)
        # XXX: Yet another painful hack.
        if not isinstance(ret, OutputEvent):
            abort(404)
        return ret

    @auth_required(with_perm=False)
    @api.doc(summary='Get event output by ID')
    @api.response(OutputEventSchema)
    def get(self, output_id):
        """Return an item from its ID"""
        item = self._get_item(output_id)
        return item

    @auth_required(roles=['chuck', 'module_data_processor'], with_perm=False)
    @api.doc(summary='Update an existing event output')
    @api.arguments(OutputEventSchema)
    @api.response(OutputEventSchema)
    def put(self, update_data, output_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(output_id)
        check_etag(item, OutputEventSchema)
        # Update, save and return item
        OutputEventSchema().update_obj(item, update_data)
        db_accessor.update(item)
        return item

    @auth_required(roles=['chuck', 'module_data_processor'], with_perm=False)
    @api.doc(summary='Delete a event output')
    @api.response(code=204)
    def delete(self, output_id):
        """Delete an item from its ID"""
        item = self._get_item(output_id)
        check_etag(item, OutputEventSchema)
        db_accessor.delete(item)


@api.route('/timeseries/')
class OutputTS(MethodView):
    """OutputTimeSerie resources endpoint"""

    @auth_required(with_perm=False)
    @api.doc(summary='List timeseries outputs')
    @api.arguments(OutputQueryArgsSchema, location='query')
    @api.response(OutputTSSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return timeseries output list"""
        # XXX: This is getting really scary.
        args['kind'] = 'http://bemserver.org/services#TimeSeries'
        return db_accessor.get_list(Output, args)

    @auth_required(roles=['chuck', 'module_data_provider'], with_perm=False)
    @api.doc(summary='Add a new timeseries output')
    @api.arguments(OutputTSSchema)
    @api.response(OutputTSSchema, code=201)
    def post(self, new_data):
        """Create a new timeseries output"""
        # Save and return new item
        item = OutputTSSchema().make_obj(new_data)
        db_accessor.create(item)
        return item


@api.route('/timeseries/<uuid:output_id>')
class OutputTSById(MethodView):
    """OutputTimeSerie resource endpoint"""

    def _get_item(self, output_id):
        """Get an item from its ID"""
        ret = db_accessor.get_item_by_id(Output, output_id)
        # XXX: Enough. My eyes are bleeding.
        if not isinstance(ret, OutputTimeSeries):
            abort(404)
        return ret

    @auth_required(with_perm=False)
    @api.doc(summary='Get timeseries output by ID')
    @api.response(OutputTSSchema)
    def get(self, output_id):
        """Return an item from its ID"""
        item = self._get_item(output_id)
        return item

    @auth_required(roles=['chuck'], with_perm=False)
    @api.doc(summary='Update an existing timeseries output')
    @api.arguments(OutputTSSchema)
    @api.response(OutputTSSchema)
    def put(self, update_data, output_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(output_id)
        check_etag(item, OutputTSSchema)
        # Update, save and return item
        OutputTSSchema().update_obj(item, update_data)
        db_accessor.update(item)
        return item

    @auth_required(roles=['chuck'], with_perm=False)
    @api.doc(summary='Delete a timeseries output')
    @api.response(code=204)
    def delete(self, output_id):
        """Delete an item from its ID"""
        item = self._get_item(output_id)
        check_etag(item, OutputTSSchema)
        db_accessor.delete(item)
