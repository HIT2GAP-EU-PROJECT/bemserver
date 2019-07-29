"""Api facades module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('facades', __name__, url_prefix='/facades',
               description='Operations on facades')


def init_app(app):
    # pylint: disable=unused-variable
    """Initialize application with module"""

    from . import views

    rest_api.register_blueprint(bp)
