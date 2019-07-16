"""Api models module views"""

from flask.views import MethodView

from . import bp as api
from .schemas import ModelSchema, ModelQueryArgsSchema

from ...extensions.rest_api import Page, check_etag
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required

from ....models import Model


@api.route('/')
class Models(MethodView):
    """Model resources endpoint"""

    @auth_required(with_perm=False)
    @api.doc(summary='List models')
    @api.arguments(ModelQueryArgsSchema, location='query')
    @api.response(ModelSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return model list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        return db_accessor.get_list(Model, args, sort)

    @auth_required(
        roles=['chuck', 'module_data_provider', 'module_data_processor'],
        with_perm=False)
    @api.doc(summary='Add a new model')
    @api.arguments(ModelSchema)
    @api.response(ModelSchema, code=201)
    def post(self, new_data):
        """Create a new model"""
        # Save and return new item
        item = ModelSchema().make_obj(new_data)
        db_accessor.create(item)
        return item


@api.route('/<uuid:model_id>')
class ModelsById(MethodView):
    """Model resource endpoint"""

    def _get_item(self, model_id):
        """Get an item from its ID"""
        return db_accessor.get_item_by_id(Model, model_id)

    @auth_required(with_perm=False)
    @api.doc(summary='Get model by ID')
    @api.response(ModelSchema)
    def get(self, model_id):
        """Return an item from its ID"""
        item = self._get_item(model_id)
        return item

    @auth_required(roles=['chuck', 'module_data_processor'], with_perm=False)
    @api.doc(summary='Update an existing model')
    @api.arguments(ModelSchema)
    @api.response(ModelSchema)
    def put(self, update_data, model_id):
        """Update an item from its ID and return updated item"""
        item = self._get_item(model_id)
        check_etag(item, ModelSchema)
        # Update, save and return item
        ModelSchema().update_obj(item, update_data)
        db_accessor.update(item)
        return item

    @auth_required(roles=['chuck', 'module_data_processor'], with_perm=False)
    @api.doc(summary='Delete a model')
    @api.response(code=204)
    def delete(self, model_id):
        """Delete an item from its ID"""
        item = self._get_item(model_id)
        check_etag(item, ModelSchema)
        db_accessor.delete(item)
