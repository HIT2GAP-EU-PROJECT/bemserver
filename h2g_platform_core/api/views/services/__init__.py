"""Api services module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('services', __name__, url_prefix='/services',
               description='Operations on services')


def init_app(app):
    # pylint: disable=unused-variable
    """Initialize application with module"""

    from . import views
    rest_api.register_blueprint(bp)
