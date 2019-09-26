"""Api windows module initialization"""

from bemserver.api.extensions.rest_api import rest_api, Blueprint


bp = Blueprint('windows', __name__, url_prefix='/windows',
               description='Operations on windows')


def init_app(app):
    """Initialize application with module"""

    from . import views

    rest_api.register_blueprint(bp)
