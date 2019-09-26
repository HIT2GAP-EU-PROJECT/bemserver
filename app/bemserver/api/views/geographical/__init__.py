"""Api geographical information initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('geographical', __name__, url_prefix='/geographical',
               description='Geographical information')


def init_app(app):
    """Initialize application with module"""

    from . import views

    rest_api.register_blueprint(bp)
