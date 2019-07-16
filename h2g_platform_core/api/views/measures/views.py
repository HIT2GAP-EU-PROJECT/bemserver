"""Api Measures module views"""

from flask.views import MethodView

from . import bp as api

from .schemas import (
    MeasureSchemaView, MeasureRequestBodySchema,
    MeasureEtagSchema, MeasureQueryArgsSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Measure, Sensor
from ..schemas import TreeSchemaView
from ....database.db_enums import DBEnumHandler


@api.route('/observation_types/')
class ObservationTypes(MethodView):
    """Observation types endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List all observation types.')
    @api.response(TreeSchemaView)
    def get(self):
        """Return observation type list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_observation_types()


@api.route('/medium_types/')
class MediumTypes(MethodView):
    """Medium types endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List all medium types.')
    @api.response(TreeSchemaView)
    def get(self):
        """Return medium type list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_medium_types()


@api.route('/units/')
class Units(MethodView):
    """Units endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List all units.')
    @api.response(TreeSchemaView)
    def get(self):
        """Return unit list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_units()


@api.route('/')
class Measures(MethodView):
    """Measure resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List measures')
    @api.arguments(MeasureQueryArgsSchema, location='query')
    @api.response(
        MeasureSchemaView(many=True), etag_schema=MeasureEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return measure list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            # XXX: find a way to do a better permissions filtering
            measures = db_accessor.get_list(Measure, args, sort)
            result = []
            for measure in measures:
                site_id = db_accessor.get_parent(Measure, measure.id)
                if site_id in uacc.sites:
                    result.append(measure)
            return result
        return db_accessor.get_list(Measure, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Add a new measure')
    @api.arguments(MeasureRequestBodySchema)
    @api.response(
        MeasureSchemaView, code=201, etag_schema=MeasureEtagSchema)
    def post(self, new_data):
        """Create a new measure"""
        # Save and return new item
        item = MeasureRequestBodySchema().make_obj(new_data)
        # permissions checks
        site_id = db_accessor.get_parent(Sensor, item.sensor_id)
        verify_scope(sites=[site_id])
        item_id = db_accessor.create(item)
        # get element
        out_item = db_accessor.get_item_by_id(Measure, item_id)
        set_etag(out_item)
        return out_item


@api.route('/<uuid:measure_id>')
class MeasureById(MethodView):
    """Measure resource endpoint"""

    # @response also uses _get_item to generate etag value
    def _get_item(self, measure_id):
        """Get an item from its ID"""
        # permissions checks
        site_id = db_accessor.get_parent(Measure, measure_id)
        verify_scope(sites=[site_id])
        return db_accessor.get_item_by_id(Measure, measure_id)

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='Get measure by ID')
    @api.response(MeasureSchemaView, etag_schema=MeasureEtagSchema)
    def get(self, measure_id):
        """Return an item from its ID"""
        item = self._get_item(measure_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing measure')
    @api.arguments(MeasureRequestBodySchema)
    @api.response(MeasureSchemaView, etag_schema=MeasureEtagSchema)
    def put(self, update_data, measure_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(measure_id)
        check_etag(item)
        # Update, save and return item
        MeasureRequestBodySchema().update_obj(item, update_data)
        db_accessor.update(item)
        # get element
        out_item = db_accessor.get_item_by_id(Measure, measure_id)
        set_etag(out_item)
        return out_item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a measure')
    @api.response(code=204, etag_schema=MeasureEtagSchema)
    def delete(self, measure_id):
        """Delete an item from its ID"""
        item = self._get_item(measure_id)
        check_etag(item)
        db_accessor.delete(item)
