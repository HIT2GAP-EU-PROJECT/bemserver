"""Api anonymous occupant users module initialization."""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('occupant_users', __name__, url_prefix='/occupant_users',
               description="Anonymous occupant users")


def init_app(app):
    """Initialize application with module"""
    from . import views  # noqa

    rest_api.register_blueprint(bp)
