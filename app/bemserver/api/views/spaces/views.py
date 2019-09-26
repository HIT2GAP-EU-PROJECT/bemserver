"""Api spaces module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    SpaceSchemaView,
    SpaceQueryArgsSchema, SpaceRequestBodySchema,
    SpaceEtagSchema)

from ..schemas import TreeSchemaView

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Space, Floor

from ....database.db_enums import DBEnumHandler


@api.route('/types/')
class SpaceTypes(MethodView):
    """Space types endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='List space types',
        description='''Space types is an arborescent structure: a space of
            a type A1 is also of type A, for A1 a subtype of A.''')
    @api.response(TreeSchemaView)
    def get(self):
        """Return space type list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_space_types()


@api.route('/')
class Spaces(MethodView):
    """Space resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List spaces')
    @api.arguments(SpaceQueryArgsSchema, location='query')
    @api.response(
        SpaceSchemaView(many=True), etag_schema=SpaceEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return space list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            args['sites'] = uacc.sites
        return db_accessor.get_list(Space, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Add a new space')
    @api.arguments(SpaceRequestBodySchema)
    @api.response(SpaceSchemaView, code=201, etag_schema=SpaceEtagSchema)
    def post(self, new_data):
        """Create a new space"""
        # Save and return new item
        item = SpaceSchemaView().make_obj(new_data)
        # permissions checks
        site_id = db_accessor.get_parent(Floor, item.floor_id)
        verify_scope(sites=[site_id])
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:space_id>')
class SpacesById(MethodView):
    """Space resource endpoint"""

    def _get_item(self, space_id):
        """Get item from id."""
        # permissions checks
        site_id = db_accessor.get_parent(Space, space_id)
        verify_scope(sites=[site_id])
        return db_accessor.get_item_by_id(Space, space_id)

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='Get space by ID')
    @api.response(SpaceSchemaView, etag_schema=SpaceEtagSchema)
    def get(self, space_id):
        """Return an item from its ID"""
        item = self._get_item(space_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing space')
    @api.arguments(SpaceRequestBodySchema)
    @api.response(SpaceSchemaView, etag_schema=SpaceEtagSchema)
    def put(self, update_data, space_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(space_id)
        check_etag(item)
        # Update, save and return item
        SpaceSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a space')
    @api.response(code=204, etag_schema=SpaceEtagSchema)
    def delete(self, space_id):
        """Delete an item from its ID"""
        item = self._get_item(space_id)
        check_etag(item)
        db_accessor.delete(item)
