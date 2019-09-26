"""Api measures module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('sensors', __name__, url_prefix='/sensors',
               description="Operations on sensors")


def init_app(app):
    """Initialize application with module"""

    from . import views  # noqa

    rest_api.register_blueprint(bp)
