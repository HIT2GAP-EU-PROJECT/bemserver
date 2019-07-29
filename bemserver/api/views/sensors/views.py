"""Api Measures module views"""

from flask.views import MethodView

from . import bp as api

from .schemas import (
    SensorSchemaView, SensorRequestBodySchema,
    SensorEtagSchema, SensorQueryArgsSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account


from ....models import Sensor, Building, Floor, Space


@api.route('/')
class Sensors(MethodView):
    """Sensor resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List sensors')
    @api.arguments(SensorQueryArgsSchema, location='query')
    @api.response(
        SensorSchemaView(many=True), etag_schema=SensorEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return list of sensors"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            # XXX: find a way to do a better permissions filtering
            sensors = db_accessor.get_list(Sensor, args, sort)
            result = []
            for sensor in sensors:
                site_id = db_accessor.get_parent(Sensor, sensor.id)
                if site_id in uacc.sites:
                    result.append(sensor)
            return result
        return db_accessor.get_list(Sensor, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Add a new sensor')
    @api.arguments(SensorRequestBodySchema)
    @api.response(
        SensorSchemaView, code=201, etag_schema=SensorEtagSchema)
    def post(self, new_data):
        """Create a new sensor"""
        # Save and return new item
        item = SensorSchemaView().make_obj(new_data)
        # permissions checks
        site_id = item.localization.site_id
        if site_id is None:
            site_id = db_accessor.get_parent(
                Building, item.localization.building_id)
        if site_id is None:
            site_id = db_accessor.get_parent(Floor, item.localization.floor_id)
        if site_id is None:
            site_id = db_accessor.get_parent(Space, item.localization.space_id)
        verify_scope(sites=[site_id])
        db_accessor.create(item)
        set_etag(item)
        return item


@api.route('/<uuid:sensor_id>')
class SensorById(MethodView):
    """Sensor resource endpoint"""

    def _get_item(self, sensor_id):
        """Get an item from its ID"""
        # permissions checks
        site_id = db_accessor.get_parent(Sensor, sensor_id)
        verify_scope(sites=[site_id])
        return db_accessor.get_item_by_id(Sensor, sensor_id)

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='Get sensor by ID')
    @api.response(SensorSchemaView, etag_schema=SensorEtagSchema)
    def get(self, sensor_id):
        """Return an item from its ID"""
        item = self._get_item(sensor_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing sensor')
    @api.arguments(SensorRequestBodySchema)
    @api.response(SensorSchemaView, etag_schema=SensorEtagSchema)
    def put(self, update_data, sensor_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(sensor_id)
        check_etag(item)
        # Update, save and return item
        SensorSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a sensor')
    @api.response(code=204, etag_schema=SensorEtagSchema)
    def delete(self, sensor_id):
        """Delete an item from its ID"""
        item = self._get_item(sensor_id)
        check_etag(item)
        db_accessor.delete(item)
