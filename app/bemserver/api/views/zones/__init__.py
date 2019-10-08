"""Api zones module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('zones', __name__, url_prefix='/zones',
               description="""Operations on zones.<br>A zone is a **logical**
               entity, not a physical one. Zones can be created by managers,
               module developers, and all users of BEMServer to ease their work
               by aggregating spaces. For instance, if a heating system only
               performs on some of the spaces in a building but not all of
               them, a zone can be created to point to this set of spaces.<br>
               To create a zone, one can specify the spaces to be contained in,
               or others already existing zones.<br><br>
               *In the current version of BEMServer, the use of zones is not
               fully functional, and may not act as described. For instance,
               it is currently not possible to list the sensors for a given
               zone.*""")


def init_app(app):
    """Initialize application with module"""

    from . import views
    rest_api.register_blueprint(bp)
