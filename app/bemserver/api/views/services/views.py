"""Api services module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import ServiceSchema, ServiceQueryArgsSchema

from ...extensions.rest_api import Page, check_etag, abort
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Service
# from ..schemas import TreeSchemaView
# from ....database.db_enums import DBEnumHandler


# TODO
# @api.route('/types/')
# class ServiceTypes(MethodView):
#     """Service types endpoint"""
#
#     @api.doc(summary='List service types')
#     @api.response(TreeSchemaView)
#     def get(self):
#         """Return service type list"""
#         dbhandler = DBEnumHandler()
#         return dbhandler.get_service_types()


@api.route('/')
class Services(MethodView):
    """Service resources endpoint"""

    @auth_required()
    @api.doc(summary='List services')
    @api.arguments(ServiceQueryArgsSchema, location='query')
    @api.response(ServiceSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return service list"""
        services = db_accessor.get_list(Service, args)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            return [
                svc for svc in services
                # verify_scope can not do the job here
                if len(set(uacc.sites).intersection(
                    set(str(site_id) for site_id in svc.site_ids))) > 0]
        return services

    @auth_required(roles=['chuck', 'module_data_provider'])
    @api.doc(summary='Add a new service')
    @api.arguments(ServiceSchema)
    @api.response(ServiceSchema, code=201)
    def post(self, new_data):
        """Create a new service"""
        # Save and return new item
        item = ServiceSchema().make_obj(new_data)
        # permissions checks
        verify_scope(sites=item.site_ids)
        db_accessor.create(item)
        return item


@api.route('/<uuid:service_id>')
class ServicesById(MethodView):
    """Service resource endpoint"""

    def _get_item(self, service_id):
        """Get an item from its ID"""
        return db_accessor.get_item_by_id(Service, service_id)

    @auth_required()
    @api.doc(summary='Get service by ID')
    @api.response(ServiceSchema)
    def get(self, service_id):
        """Return an item from its ID"""
        item = self._get_item(service_id)
        # permissions checks
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            if len(set(uacc.sites).intersection(
                    set(str(site_id) for site_id in item.site_ids))) <= 0:
                abort(403)
        return item

    @auth_required(roles=['chuck'], with_perm=False)
    @api.doc(summary='Update an existing service')
    @api.arguments(ServiceSchema)
    @api.response(ServiceSchema)
    def put(self, update_data, service_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(service_id)
        check_etag(item, ServiceSchema)
        # Update, save and return item
        ServiceSchema().update_obj(item, update_data)
        db_accessor.update(item)
        return item

    @auth_required(roles=['chuck'], with_perm=False)
    @api.doc(summary='Delete a service')
    @api.response(code=204)
    def delete(self, service_id):
        """Delete an item from its ID"""
        item = self._get_item(service_id)
        check_etag(item, ServiceSchema)
        db_accessor.delete(item)
