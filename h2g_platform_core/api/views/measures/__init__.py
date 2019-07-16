"""Api measures module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('measures', __name__, url_prefix='/measures',
               description="Operations on measures")


def init_app(app):
    # pylint: disable=unused-variable
    """Initialize application with module"""

    from . import views  # noqa

    rest_api.register_blueprint(bp)
