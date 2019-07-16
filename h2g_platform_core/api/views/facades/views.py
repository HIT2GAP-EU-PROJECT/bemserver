"""Api facades module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    FacadeSchemaView,
    FacadeQueryArgsSchema, FacadeRequestBodySchema,
    FacadeEtagSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Facade, Building


@api.route('/')
class Facades(MethodView):
    """Facade resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List facades')
    @api.arguments(FacadeQueryArgsSchema, location='query')
    @api.response(
        FacadeSchemaView(many=True), etag_schema=FacadeEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return facade list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            # XXX: find a way to do a better permissions filtering
            facades = db_accessor.get_list(Facade, args, sort)
            result = []
            for facade in facades:
                site_id = db_accessor.get_parent(Facade, facade.id)
                if site_id in uacc.sites:
                    result.append(facade)
            return result
        return db_accessor.get_list(Facade, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Add a new facade')
    @api.arguments(FacadeRequestBodySchema)
    @api.response(FacadeSchemaView, code=201, etag_schema=FacadeEtagSchema)
    def post(self, new_data):
        """Create a new facade"""
        # Save and return new item
        item = FacadeSchemaView().make_obj(new_data)
        # permissions checks
        site_id = db_accessor.get_parent(Building, item.building_id)
        verify_scope(sites=[site_id])
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:facade_id>')
class FacadesById(MethodView):
    """Facade resource endpoint"""
    def _get_item(self, facade_id):
        """Get an item from its ID"""
        # permissions checks
        site_id = db_accessor.get_parent(Facade, facade_id)
        verify_scope(sites=[site_id])
        return db_accessor.get_item_by_id(Facade, facade_id)

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='Get facade by ID')
    @api.response(FacadeSchemaView, etag_schema=FacadeEtagSchema)
    def get(self, facade_id):
        """Return an item from its ID"""
        item = self._get_item(facade_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing facade')
    @api.arguments(FacadeRequestBodySchema)
    @api.response(FacadeSchemaView, etag_schema=FacadeEtagSchema)
    def put(self, update_data, facade_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(facade_id)
        check_etag(item)
        # Update, save and return item
        FacadeSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a facade')
    @api.response(code=204, etag_schema=FacadeEtagSchema)
    def delete(self, facade_id):
        """Delete an item from its ID"""
        item = self._get_item(facade_id)
        check_etag(item)
        db_accessor.delete(item)
