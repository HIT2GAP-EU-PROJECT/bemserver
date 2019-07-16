"""Api slabs module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    SlabSchemaView,
    SlabQueryArgsSchema, SlabRequestBodySchema,
    SlabEtagSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Slab, Building
from ..schemas import TreeSchemaView
from ....database.db_enums import DBEnumHandler


@api.route('/types/')
class SlabTypes(MethodView):
    """Slab types endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List slab types')
    @api.response(TreeSchemaView)
    def get(self):
        """Return slab type list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_slab_types()


@api.route('/')
class Slabs(MethodView):
    """Slab resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List slabs')
    @api.arguments(SlabQueryArgsSchema, location='query')
    @api.response(
        SlabSchemaView(many=True), etag_schema=SlabEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return slab list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            # XXX: find a way to do a better permissions filtering
            slabs = db_accessor.get_list(Slab, args, sort)
            result = []
            for slab in slabs:
                site_id = db_accessor.get_parent(Building, slab.building_id)
                if site_id in uacc.sites:
                    result.append(slab)
            return result
        return db_accessor.get_list(Slab, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Add a new slab')
    @api.arguments(SlabRequestBodySchema)
    @api.response(SlabSchemaView, code=201, etag_schema=SlabEtagSchema)
    def post(self, new_data):
        """Create a new slab"""
        # Save and return new item
        item = SlabSchemaView().make_obj(new_data)
        # permissions checks
        site_id = db_accessor.get_parent(Building, item.building_id)
        verify_scope(sites=[site_id])
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:slab_id>')
class SlabsById(MethodView):
    """Slab resource endpoint"""
    def _get_item(self, slab_id):
        """Get an item from its ID"""
        # permissions checks
        site_id = db_accessor.get_parent(Slab, slab_id)
        verify_scope(sites=[site_id])
        return db_accessor.get_item_by_id(Slab, slab_id)

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='Get slab by ID')
    @api.response(SlabSchemaView, etag_schema=SlabEtagSchema)
    def get(self, slab_id):
        """Return an item from its ID"""
        item = self._get_item(slab_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing slab')
    @api.arguments(SlabRequestBodySchema)
    @api.response(SlabSchemaView, etag_schema=SlabEtagSchema)
    def put(self, update_data, slab_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(slab_id)
        check_etag(item)
        # Update, save and return item
        SlabSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a slab')
    @api.response(code=204, etag_schema=SlabEtagSchema)
    def delete(self, slab_id):
        """Delete an item from its ID"""
        item = self._get_item(slab_id)
        check_etag(item)
        db_accessor.delete(item)
