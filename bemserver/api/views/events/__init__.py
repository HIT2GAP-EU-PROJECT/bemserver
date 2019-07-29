"""Api events module initialization"""

from bemserver.api.extensions.rest_api import rest_api, Blueprint

from bemserver.models.events import EventCategory


DESCRIPTION = """Operations on events. An event is typically an output sent by
a service plugged to BEMServer, to BEMServer. This enables interoperability
between different services on two different types of data:

+ timeseries: for instance a forecasting module can send predicted values
+ events: for instance a fault detection module can send information on
identified errors in the HVAC systems.

Some important features of events are:

+ the ID of the service that generated it, and potentially the ID of the model used. **These IDs must refer to the ones in the `/services` (resp. `/models`) APIs.**
+ the ID of (at least) the site to which the event relates: a location must be associated to an event, and the more accurate it is, the better it is for other modules to filter in them.
+ a level of criticity. Possible criticity levels are, from least to most important: INFO, WARNING, ERROR, CRITICAL.
+ a category, which is the most important feature on events.

```
{}
```

A category may be used if the subcategory is not known or if no subcategory applies.
""".format(EventCategory.build_hierarchy_tree_human())


bp = Blueprint('events', __name__, url_prefix='/events',
               description=DESCRIPTION)


def init_app(app):
    # pylint: disable=unused-variable
    """Initialize application with module"""

    from . import views

    rest_api.register_blueprint(bp)
