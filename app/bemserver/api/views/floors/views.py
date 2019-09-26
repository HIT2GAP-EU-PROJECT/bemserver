"""Api floors module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    FloorSchemaView,
    FloorQueryArgsSchema, FloorRequestBodySchema,
    FloorEtagSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Floor, Building
from ..schemas import TreeSchemaView
from ....database.db_enums import DBEnumHandler


@api.route('/types/')
class FloorTypes(MethodView):
    """Floor types endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='List floor types',
        description=(
            'Floor types is an arborescent structure: a floor of '
            'a type A1 is also of type A, for A1 a subtype of A.'))
    @api.response(TreeSchemaView)
    def get(self):
        """Return floor type list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_floor_types()


@api.route('/')
class Floors(MethodView):
    """Floor resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='List floors',
        description='''Allow one to get the description of different floors.
            Filters can and shall be used as parameters.''')
    @api.arguments(FloorQueryArgsSchema, location='query')
    @api.response(
        FloorSchemaView(many=True), etag_schema=FloorEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return floor list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            args['sites'] = uacc.sites
        return db_accessor.get_list(Floor, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Add a new floor',
        description='''Create a new floor in BEMServer.<br>**A building needs to
            be created first!**''')
    @api.arguments(FloorRequestBodySchema)
    @api.response(FloorSchemaView, code=201, etag_schema=FloorEtagSchema)
    def post(self, new_data):
        """Create a new floor"""
        # Save and return new item
        item = FloorSchemaView().make_obj(new_data)
        # permissions checks
        site_id = db_accessor.get_parent(Building, item.building_id)
        verify_scope(sites=[site_id])
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:floor_id>')
class FloorsById(MethodView):
    """Floor resource endpoint"""

    # @response also uses _get_item to generate etag value
    def _get_item(self, floor_id):
        """Get an item from its ID"""
        # permissions checks
        site_id = db_accessor.get_parent(Floor, floor_id)
        verify_scope(sites=[site_id])
        return db_accessor.get_item_by_id(Floor, floor_id)

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='Get floor by ID')
    @api.response(FloorSchemaView, etag_schema=FloorEtagSchema)
    def get(self, floor_id):
        """Return an item from its ID"""
        item = self._get_item(floor_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing floor')
    @api.arguments(FloorRequestBodySchema)
    @api.response(FloorSchemaView, etag_schema=FloorEtagSchema)
    def put(self, update_data, floor_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(floor_id)
        check_etag(item)
        # Update, save and return item
        FloorSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a floor')
    @api.response(code=204, etag_schema=FloorEtagSchema)
    def delete(self, floor_id):
        """Delete an item from its ID"""
        item = self._get_item(floor_id)
        check_etag(item)
        db_accessor.delete(item)
