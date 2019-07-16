"""Api windows module initialization"""

from h2g_platform_core.api.extensions.rest_api import rest_api, Blueprint


bp = Blueprint('windows', __name__, url_prefix='/windows',
               description='Operations on windows')


def init_app(app):
    """Initialize application with module"""

    from . import views  # pylint: disable=unused-variable

    rest_api.register_blueprint(bp)
