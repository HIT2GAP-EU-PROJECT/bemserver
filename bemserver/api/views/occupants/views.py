"""Api occupants module views (authentication protected endpoints)."""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    OccupantSchemaView, OccupantRequestBodySchema,
    OccupantEtagSchema, OccupantQueryArgsSchema,
    AgeCategorySchemaView,
    OccupantWorkspaceTypeSchemaView, OccupantDistanceToPointTypeSchemaView,
    OccupantKnowledgeLevelSchemaView, OccupantActivityFrequencySchemaView)
from ..schemas import TreeSchemaView

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.rest_api.doc_responses import build_responses
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required

from ....database.db_enums import DBEnumHandler

from ....models import (
    Occupant, AgeCategory, WorkspaceType, DistanceToPointType,
    KnowledgeLevel, ActivityFrequency)


@api.route('/gender_types/')
class OccupantGenderType(MethodView):
    """Occupant gender types endpoint"""

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(summary='List gender types')
    @api.response(TreeSchemaView)
    def get(self):
        """Return gender type list"""
        dbhandler = DBEnumHandler()
        return dbhandler.get_gender_types()


@api.route('/age_categories/')
class OccupantAgeCategory(MethodView):
    """Occupant age categories endpoint"""

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(summary='List age categories')
    @api.response(AgeCategorySchemaView(many=True))
    @api.paginate(Page)
    def get(self):
        """Return age category type list"""
        return list(AgeCategory)


@api.route('/workspace_types/')
class OccupantWorkspaceType(MethodView):
    """Occupant workspace types endpoint"""

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(summary='List workspace types')
    @api.response(OccupantWorkspaceTypeSchemaView(many=True))
    @api.paginate(Page)
    def get(self):
        """Return workspace type list"""
        return list(WorkspaceType)


@api.route('/distancetopoint_types/')
class OccupantDistanceToPointType(MethodView):
    """Occupant distance to point types endpoint"""

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(summary='List distance to point types')
    @api.response(OccupantDistanceToPointTypeSchemaView(many=True))
    @api.paginate(Page)
    def get(self):
        """Return distance to point type list"""
        return list(DistanceToPointType)


@api.route('/knowledge_levels/')
class OccupantKnowledgeLevel(MethodView):
    """Occupant knowledge levels endpoint"""

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(summary='List knowledge levels')
    @api.response(OccupantKnowledgeLevelSchemaView(many=True))
    @api.paginate(Page)
    def get(self):
        """Return knowledge level list"""
        return list(KnowledgeLevel)


@api.route('/activity_frequencies/')
class OccupantActivityFrequency(MethodView):
    """Occupant activity frequencies endpoint"""

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(summary='List activity frequencies')
    @api.response(OccupantActivityFrequencySchemaView(many=True))
    @api.paginate(Page)
    def get(self):
        """Return activity frequency list"""
        return list(ActivityFrequency)


@api.route('/')
class Occupants(MethodView):
    """Occupant resources endpoint"""

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(
        summary='List occupants',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.arguments(OccupantQueryArgsSchema, location='query')
    @api.response(
        OccupantSchemaView(many=True),
        etag_schema=OccupantEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return occupant list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        return db_accessor.get_list(Occupant, args, sort)

    @auth_required(roles=['anonymous_occupant'])
    @api.doc(
        summary='Add a new occupant',
        responses=build_responses([201, 404, 422, 500])
    )
    @api.arguments(OccupantRequestBodySchema)
    @api.response(OccupantSchemaView, code=201, etag_schema=OccupantEtagSchema)
    def post(self, new_data):
        """Create a new occupant"""
        # Save and return new item
        item = OccupantSchemaView().make_obj(new_data)
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:occupancy_id>')
class OccupantById(MethodView):
    """Occupant resource endpoint"""

    # @api.response also uses _get_item to generate etag value
    def _get_item(self, occupancy_id):
        """Get an item from its ID"""
        return db_accessor.get_item_by_id(Occupant, occupancy_id)

    @auth_required(roles=[
        'anonymous_occupant', 'building_manager', 'module_data_processor'])
    @api.doc(
        summary='Get occupant by ID',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.response(OccupantSchemaView, etag_schema=OccupantEtagSchema)
    def get(self, occupancy_id):
        """Return an item from its ID"""
        item = self._get_item(occupancy_id)
        set_etag(item)
        return item

    @auth_required(roles=['anonymous_occupant'])
    @api.doc(
        summary='Update an existing occupant',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.arguments(OccupantRequestBodySchema)
    @api.response(OccupantSchemaView, etag_schema=OccupantEtagSchema)
    def put(self, update_data, occupancy_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(occupancy_id)
        check_etag(item)
        # Update, save and return item
        OccupantSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['anonymous_occupant'])
    @api.doc(
        summary='Delete an occupant',
        responses=build_responses([204, 404, 422, 500])
    )
    @api.response(code=204, etag_schema=OccupantEtagSchema)
    def delete(self, occupancy_id):
        """Delete an item from its ID"""
        item = self._get_item(occupancy_id)
        check_etag(item)
        db_accessor.delete(item)
