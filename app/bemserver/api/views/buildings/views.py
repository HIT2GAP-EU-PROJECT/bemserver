"""Api buildings module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    BuildingSchemaView, BuildingQueryArgsSchema, BuildingRequestBodySchema,
    BuildingEtagSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Building
from ..schemas import TreeSchemaView
from ....database.db_enums import DBEnumHandler


@api.route('/types/')
class BuildingTypes(MethodView):
    """Building types endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='''List all building types.''',
        description='''Building types is an arborescent structure: a building of
            a type A1 is also of type A, for A1 a subtype of A.''')
    @api.response(TreeSchemaView)
    def get(self):
        """Return building type list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_building_types()


@api.route('/')
class Buildings(MethodView):
    """Building resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='List buildings',
        description='''Allow one to get the description of different buildings.
            Different filters can be used as parameters.''')
    @api.arguments(BuildingQueryArgsSchema, location='query')
    @api.response(BuildingSchemaView(many=True),
                  etag_schema=BuildingEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return building list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            args['sites'] = uacc.sites
        return db_accessor.get_list(Building, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Add a new building',
        description='''Create a new building in BEMServer.<br>**A site needs to
            be created first!**''')
    @api.arguments(BuildingRequestBodySchema)
    @api.response(
        BuildingSchemaView, code=201, etag_schema=BuildingEtagSchema)
    def post(self, new_data):
        """Create a new building"""
        # Save and return new item
        item = BuildingSchemaView().make_obj(new_data)
        # permissions checks
        verify_scope(sites=[item.site_id])
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:building_id>')
class BuildingsById(MethodView):
    """Building resource endpoint"""

    def _get_item(self, building_id):
        """Get an item from its ID"""
        item = db_accessor.get_item_by_id(Building, building_id)
        # permissions checks
        verify_scope(sites=[item.site_id])
        return item

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='Get building by ID',
        description='Get a unique building based on its UUID.')
    @api.response(BuildingSchemaView, etag_schema=BuildingEtagSchema)
    def get(self, building_id):
        """Return an item from its ID"""
        item = self._get_item(building_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Update an existing building',
        description='Update a building from its UUID and return updated data.')
    @api.arguments(BuildingRequestBodySchema)
    @api.response(BuildingSchemaView, etag_schema=BuildingEtagSchema)
    def put(self, update_data, building_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(building_id)
        check_etag(item)
        # Update, save and return item
        BuildingSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a building')
    @api.response(code=204, etag_schema=BuildingEtagSchema)
    def delete(self, building_id):
        """Delete an item from its ID"""
        item = self._get_item(building_id)
        check_etag(item)
        db_accessor.delete(item)
