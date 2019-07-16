"""Api IFC module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('ifc', __name__, url_prefix='/ifc',
               description="Operations on IFC files")


def init_app(app):
    """Initialize application with module"""

    from . import views

    rest_api.register_blueprint(bp)
