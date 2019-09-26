"""Api spaces module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('spaces', __name__, url_prefix='/spaces',
               description='''Operations on spaces.<br>A space can be a room (
               a physically separated space) or not.
               ''')


def init_app(app):
    """Initialize application with module"""

    from . import views

    rest_api.register_blueprint(bp)
