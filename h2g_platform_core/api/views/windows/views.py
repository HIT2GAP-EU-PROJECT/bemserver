"""Api windows module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    WindowSchemaView,
    WindowQueryArgsSchema, WindowRequestBodySchema,
    WindowEtagSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Window, Facade
from ..schemas import TreeSchemaView
from ....database.db_enums import DBEnumHandler


@api.route('/covering_types/')
class WindowCoveringTypes(MethodView):
    """Window covering types endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List window covering types')
    @api.response(TreeSchemaView)
    def get(self):
        """Return window covering type list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_window_covering_types()


@api.route('/')
class Windows(MethodView):
    """Window resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List windows')
    @api.arguments(WindowQueryArgsSchema, location='query')
    @api.response(
        WindowSchemaView(many=True), etag_schema=WindowEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return item list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            # XXX: find a way to do a better permissions filtering
            windows = db_accessor.get_list(Window, args, sort)
            result = []
            for window in windows:
                site_id = db_accessor.get_parent(Window, window.id)
                if site_id in uacc.sites:
                    result.append(window)
            return result
        return db_accessor.get_list(Window, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Add a new window')
    @api.arguments(WindowRequestBodySchema)
    @api.response(WindowSchemaView, code=201, etag_schema=WindowEtagSchema)
    def post(self, new_data):
        """Create a new item"""
        # Save and return new item
        item = WindowSchemaView().make_obj(new_data)
        # permissions checks
        site_id = db_accessor.get_parent(Facade, item.facade_id)
        verify_scope(sites=[site_id])
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:window_id>')
class WindowsById(MethodView):
    """Window resource endpoint"""

    def _get_item(self, window_id):
        item = db_accessor.get_item_by_id(Window, window_id)
        # permissions checks
        site_id = db_accessor.get_parent(Facade, item.facade_id)
        verify_scope(sites=[site_id])
        return item

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='Get a window by ID')
    @api.response(WindowSchemaView, etag_schema=WindowEtagSchema)
    def get(self, window_id):
        """Return an item from its ID"""
        item = self._get_item(window_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing window')
    @api.arguments(WindowRequestBodySchema)
    @api.response(WindowSchemaView, etag_schema=WindowEtagSchema)
    def put(self, update_data, window_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(window_id)
        check_etag(item)
        # Update, save and return item
        WindowSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a window')
    @api.response(code=204, etag_schema=WindowEtagSchema)
    def delete(self, window_id):
        """Delete an item from its ID"""
        item = self._get_item(window_id)
        check_etag(item)
        db_accessor.delete(item)
