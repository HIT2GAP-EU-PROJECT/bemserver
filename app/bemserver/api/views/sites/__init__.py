"""Api sites module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


bp = Blueprint('sites', __name__, url_prefix='/sites',
               description="""Operations on sites. Sites are the root elements
               of a project, so that every other elements can refer to a site.
               <br>The concept of site in BEMServer is identical to the one in
               the IFC schema. Buildings, Floors and Spaces are the following
               elements in the hierarchy:

+ a site contains one or many buildings;
+ a building contains one or many floors (buildingStorey in IFC).
+ a floor contains one or many spaces.

In BEMServer, a site is characterized by:

+ geographical information (position, hemisphere, climatic region);
+ a name
+ a description (which is optional)
               """)


def init_app(app):
    """Initialize application with module"""

    from . import views
    rest_api.register_blueprint(bp)
