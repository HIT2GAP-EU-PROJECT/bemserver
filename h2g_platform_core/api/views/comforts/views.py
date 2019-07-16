"""Api comforts module views (authentication protected endpoints)."""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    ComfortSchemaView, ComfortRequestBodySchema, ComfortEtagSchema,
    ComfortQueryArgsSchema, PreferenceTypeSchemaView, ComfortTypeSchemaView)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.rest_api.doc_responses import build_responses
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required

from ....models import Comfort, PreferenceType, ComfortType


@auth_required(roles=[
    'anonymous_occupant', 'building_manager', 'module_data_processor'])
@api.route('/preference_types/')
@api.doc(summary='List occupant comfort preference types')
@api.response(PreferenceTypeSchemaView(many=True))
@api.paginate(Page)
def get_occ_comfort_preference_types():
    """Return preference type list."""
    return list(PreferenceType)


@auth_required(roles=[
    'anonymous_occupant', 'building_manager', 'module_data_processor'])
@api.route('/comfort_types/')
@api.doc(summary='List occupant comfort types')
@api.response(ComfortTypeSchemaView(many=True))
@api.paginate(Page)
def get_occ_comfort_types():
    """Return comfort type list."""
    return list(ComfortType)


@auth_required(roles=[
    'anonymous_occupant', 'building_manager', 'module_data_processor'])
@api.route('/')
@api.doc(summary='List comforts')
@api.arguments(ComfortQueryArgsSchema, location='query')
@api.response(
    ComfortSchemaView(many=True), etag_schema=ComfortEtagSchema(many=True))
@api.paginate(Page)
def get_occ_comforts(args):
    """Return comfort list."""
    sort = args.pop('sort', None)
    return db_accessor.get_list(Comfort, args, sort)


@auth_required(roles=['anonymous_occupant'])
@api.route('/', methods=['POST'])
@api.doc(
    summary='Add a new comfort',
    responses=build_responses([201, 422, 500])
)
@api.arguments(ComfortRequestBodySchema)
@api.response(ComfortSchemaView, code=201, etag_schema=ComfortEtagSchema)
def post_occ_comforts(new_data):
    """Create a new comfort."""
    # Save and return new item
    item = ComfortSchemaView().make_obj(new_data)
    db_accessor.create(item)
    set_etag(item)
    return item


@api.route('/<uuid:comfort_id>')
class ComfortById(MethodView):
    """Comfort resource endpoint"""

    def _get_item(self, comfort_id):
        return db_accessor.get_item_by_id(Comfort, comfort_id)

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(
        summary='Get comfort by ID',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.response(ComfortSchemaView, etag_schema=ComfortEtagSchema)
    def get(self, comfort_id):
        """Return an item from its ID"""
        item = self._get_item(comfort_id)
        set_etag(item)
        return item

    @auth_required(roles=['anonymous_occupant'])
    @api.doc(
        summary='Update an existing comfort',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.arguments(ComfortRequestBodySchema)
    @api.response(ComfortSchemaView, etag_schema=ComfortEtagSchema)
    def put(self, update_data, comfort_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(comfort_id)
        check_etag(item)
        # Update, save and return item
        ComfortSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['anonymous_occupant'])
    @api.doc(
        summary='Delete a comfort',
        responses=build_responses([204, 404, 422, 500])
    )
    @api.response(code=204, etag_schema=ComfortEtagSchema)
    def delete(self, comfort_id):
        """Delete an item from its ID"""
        item = self._get_item(comfort_id)
        check_etag(item)
        db_accessor.delete(item)
