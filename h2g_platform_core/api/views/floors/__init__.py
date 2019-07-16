"""Api floors module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('floors', __name__, url_prefix='/floors',
               description='''A BEMServer floor is an horizontal layering of a
               building. It therefore relates to a building and indirectly to
               a site, and contains spaces.''')


def init_app(app):
    # pylint: disable=unused-variable
    """Initialize application with module"""

    from . import views
    rest_api.register_blueprint(bp)
