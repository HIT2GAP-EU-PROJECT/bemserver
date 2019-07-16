"""Api zones module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    ZoneSchemaView, ZoneQueryArgsSchema, ZoneRequestBodySchema,
    ZoneEtagSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Zone, Building


@api.route('/')
class Zones(MethodView):
    """Zone resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List zones')
    @api.arguments(ZoneQueryArgsSchema, location='query')
    @api.response(
        ZoneSchemaView(many=True), etag_schema=ZoneEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return zone list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            # XXX: find a way to do a better permissions filtering
            zones = db_accessor.get_list(Zone, args, sort)
            result = []
            for zone in zones:
                site_id = db_accessor.get_parent(Building, zone.building_id)
                if site_id in uacc.sites:
                    result.append(zone)
            return result
        return db_accessor.get_list(Zone, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Add a new zone')
    @api.arguments(ZoneRequestBodySchema)
    @api.response(ZoneSchemaView, code=201, etag_schema=ZoneEtagSchema)
    def post(self, new_data):
        """Create a new zone"""
        # Save and return new item
        item = ZoneSchemaView().make_obj(new_data)
        # permissions checks
        site_id = db_accessor.get_parent(Building, item.building_id)
        verify_scope(sites=[site_id])
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:zone_id>')
class ZonesById(MethodView):
    """Zone resource endpoint"""

    # @response also uses _get_item to generate etag value
    def _get_item(self, zone_id):
        """Get item from id."""
        # permissions checks
        site_id = db_accessor.get_parent(Zone, zone_id)
        verify_scope(sites=[site_id])
        return db_accessor.get_item_by_id(Zone, zone_id)

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='Get zone by ID')
    @api.response(ZoneSchemaView, etag_schema=ZoneEtagSchema)
    def get(self, zone_id):
        """Return an item from its ID"""
        item = self._get_item(zone_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing zone')
    @api.arguments(ZoneRequestBodySchema)
    @api.response(ZoneSchemaView, etag_schema=ZoneEtagSchema)
    def put(self, update_data, zone_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(zone_id)
        check_etag(item)
        # Update, save and return item
        ZoneSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a zone')
    @api.response(code=204, etag_schema=ZoneEtagSchema)
    def delete(self, zone_id):
        """Delete an item from its ID"""
        item = self._get_item(zone_id)
        check_etag(item)
        db_accessor.delete(item)
