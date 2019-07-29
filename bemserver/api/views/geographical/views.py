"""Api geographical information views"""

from flask.views import MethodView

from ...extensions.auth import auth_required

from . import bp as api
from ..schemas import TreeSchemaView
from ....database.db_enums import DBEnumHandler


@api.route('/orientations/')
class OrientationTypes(MethodView):
    """Geographical orientation types endpoint."""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List orientation types')
    @api.response(TreeSchemaView)
    def get(self):
        """Return orientation type list."""
        dbhandler = DBEnumHandler()
        return dbhandler.get_orientation_types()


@api.route('/hemispheres/')
class HemisphereTypes(MethodView):
    """Geographical hemisphere types endpoint."""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List hemisphere types')
    @api.response(TreeSchemaView)
    def get(self):
        """Return hemisphere type list."""
        dbhandler = DBEnumHandler()
        return dbhandler.get_hemisphere_types()


@api.route('/climates/')
class ClimateTypes(MethodView):
    """Geographical climate types endpoint."""

    @auth_required(roles=['building_manager', 'module_data_processor'])
    @api.doc(summary='List climate types')
    @api.response(TreeSchemaView)
    def get(self):
        """Return climate type list."""
        dbhandler = DBEnumHandler()
        return dbhandler.get_climate_types()
