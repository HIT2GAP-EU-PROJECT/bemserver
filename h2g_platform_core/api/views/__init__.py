"""Modules initialization"""


def init_app(app):
    """Initialize application by registering views"""

    if app.config.get('MAINTENANCE_MODE'):
        return

    # authentication API endpoints
    if (app.config['AUTHENTICATION_ENABLED']
            or app.config['AUTHENTICATION_DEMO_ENABLED']):
        from . import auth
        auth.init_app(app)

    # timeseries API endpoints
    from . import timeseries
    timeseries.init_app(app)

    # events API endpoints
    if not app.config['EVENTS_API_DISABLED']:
        from . import events
        events.init_app(app)

    # data model API endpoints
    if not app.config['DATA_MODEL_API_DISABLED']:
        from . import sites
        from . import buildings
        from . import floors
        from . import zones
        from . import spaces
        from . import facades
        from . import slabs
        from . import windows
        from . import sensors
        from . import geographical
        from . import measures
        from . import services
        from . import models
        from . import outputs
        sites.init_app(app)
        buildings.init_app(app)
        floors.init_app(app)
        zones.init_app(app)
        spaces.init_app(app)
        facades.init_app(app)
        slabs.init_app(app)
        windows.init_app(app)
        sensors.init_app(app)
        geographical.init_app(app)
        measures.init_app(app)
        services.init_app(app)
        models.init_app(app)
        outputs.init_app(app)

        if not app.config['OCCUPANTS_API_DISABLED']:
            from . import occupant_users
            from . import occupants
            from . import comforts
            occupant_users.init_app(app)
            occupants.init_app(app)
            comforts.init_app(app)

        if not app.config['IFC_API_DISABLED']:
            from . import ifc
            ifc.init_app(app)
