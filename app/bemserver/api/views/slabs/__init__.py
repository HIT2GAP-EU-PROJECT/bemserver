"""Api slabs module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('slabs', __name__, url_prefix='/slabs',
               description='Operations on slabs')


def init_app(app):
    """Initialize application with module"""

    from . import views

    rest_api.register_blueprint(bp)
