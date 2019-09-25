"""Api buildings module initialization"""

from ...extensions.rest_api import rest_api, Blueprint

DESCRIPTION = """Operations on buildings.

A BEMServer building refers to full building structure, that is part of a
specific site, and that is made of floors.

Those endpoints allow to perform CRUD operations on buildings: Get buildings
(with different filtering possibilities); Create a building; Update an existing
one, or Delete one."""


bp = Blueprint('buildings', __name__, url_prefix='/buildings',
               description=DESCRIPTION)


def init_app(app):
    # pylint: disable=unused-variable
    """Initialize application with module"""

    from . import views
    rest_api.register_blueprint(bp)
