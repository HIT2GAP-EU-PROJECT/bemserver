"""Extensions initialization"""

from . import logger
from . import rest_api
from . import limiter
from . import maintenance


def init_app(app):
    """Initialize all application extensions"""
    # set authentication enabled default value to False
    app.config.setdefault('AUTHENTICATION_ENABLED', False)
    app.config.setdefault('AUTHENTICATION_DEMO_ENABLED', False)

    for extension in (
            logger,
            rest_api,
    ):
        extension.init_app(app)

    if app.config.get('MAINTENANCE_MODE'):
        maintenance.init_app(app)
    else:
        if (app.config['AUTHENTICATION_ENABLED']
                or app.config['AUTHENTICATION_DEMO_ENABLED']):
            from . import auth
            auth.init_app(app)
        if not app.config['EVENTS_API_DISABLED']:
            from . import relational_db
            relational_db.init_app(app)
        if not app.config['DATA_MODEL_API_DISABLED']:
            from . import database
            database.init_app(app)
        if app.config['CONCURRENT_REQUESTS_LIMITS_ENABLED']:
            limiter.init_app(app)
