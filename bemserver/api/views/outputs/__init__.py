"""Api outputs module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('outputs', __name__, url_prefix='/outputs',
               description='Operations on outputs')


def init_app(app):
    # pylint: disable=unused-variable
    """Initialize application with module"""

    from . import views
    rest_api.register_blueprint(bp)
