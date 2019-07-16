"""Api sites module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import (
    SiteSchemaView,
    SiteQueryArgsSchema, SiteRequestBodySchema,
    SiteEtagSchema)

from ...extensions.rest_api import Page, check_etag, set_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required, verify_scope, get_user_account

from ....models import Site


@api.route('/')
class Sites(MethodView):
    """Site resources endpoint"""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='List sites',
        description='''Allow one to get information on the different sites, and
            to filter on those.''')
    @api.arguments(SiteQueryArgsSchema, location='query')
    @api.response(
        SiteSchemaView(many=True), etag_schema=SiteEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return site list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        # permissions filter
        uacc = get_user_account()
        if uacc is not None and '*' not in uacc.sites:
            args['sites'] = uacc.sites
        return db_accessor.get_list(Site, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Add a new site',
        description='''Add a new site to BEMServer. Whenever a new monitored
            buildings needs to be registered, this is the first operation to
            be performed.'''
        )
    @api.arguments(SiteRequestBodySchema)
    @api.response(SiteSchemaView, code=201, etag_schema=SiteEtagSchema)
    def post(self, new_data):
        """Create a new site"""
        # Save and return new item
        item = SiteSchemaView().make_obj(new_data)
        # /!\ no permissions check, only role counts
        db_accessor.create(item)
        # TODO: just add the new site ID to allowed sites in user account
        set_etag(item)
        return item


@api.route('/<uuid:site_id>')
class SitesById(MethodView):
    """Site resource endpoint"""

    def _get_item(self, site_id):
        """Get an item from its ID"""
        # permissions checks
        verify_scope(sites=[site_id])
        return db_accessor.get_item_by_id(Site, site_id)

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(
        summary='Get site by ID',
        description='''Obtain the description of a site, obtained from it UUID.
        ''')
    @api.response(SiteSchemaView, etag_schema=SiteEtagSchema)
    def get(self, site_id):
        """Return an item from its ID"""
        item = self._get_item(site_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Update an existing site')
    @api.arguments(SiteRequestBodySchema)
    @api.response(SiteSchemaView, etag_schema=SiteEtagSchema)
    def put(self, update_data, site_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(site_id)
        check_etag(item)
        # Update, save and return item
        SiteSchemaView().update_obj(item, update_data)
        db_accessor.update(item)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(summary='Delete a site')
    @api.response(code=204, etag_schema=SiteEtagSchema)
    def delete(self, site_id):
        """Delete an item from its ID"""
        item = self._get_item(site_id)
        check_etag(item)
        db_accessor.delete(item)
