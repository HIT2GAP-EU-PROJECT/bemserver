"""Api comforts module initialization."""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('comforts', __name__, url_prefix='/comforts',
               description="Operations on occupants comforts")


def init_app(app):
    """Initialize application with module"""
    from . import views

    rest_api.register_blueprint(bp)
