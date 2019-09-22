"""Api occupants module initialization."""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('occupants', __name__, url_prefix='/occupants',
               description="Operations on occupants")


def init_app(app):
    """Initialize application with module"""
    from . import views

    rest_api.register_blueprint(bp)
