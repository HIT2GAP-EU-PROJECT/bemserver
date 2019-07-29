"""Api models module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('models', __name__, url_prefix='/models',
               description='Operations on models')


def init_app(app):
    # pylint: disable=unused-variable
    """Initialize application with module"""

    from . import views
    rest_api.register_blueprint(bp)
