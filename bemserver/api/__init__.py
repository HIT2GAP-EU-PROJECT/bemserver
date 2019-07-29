"""Application initialization"""

from flask import Flask
from flask.helpers import get_env
from flask_migrate import Migrate

from bemserver.database.relational import db

from . import extensions
from . import views


DEFAULT_CONFIG_FILE = 'bemserver.api.default_api_settings'
CONFIGS = {
    'production': 'ProductionConfig',
    'development': 'DevelopmentConfig',
}


def create_app(config_class=None):
    """Entry point to the Flask RESTful Server application."""
    kwargs = {
        'static_folder': None,  # Don't register static view
    }

    # Init Flask app
    app = Flask('BEMServer API', **kwargs)

    # A config class can be passed "manually" (typically for tests)
    # The general use case is "config_class is None". In this case, we get
    #  the fully qualified path to the class object.
    # 'from_object' can take either a class object or a path
    if config_class is None:
        config_class = '.'.join((DEFAULT_CONFIG_FILE, CONFIGS[get_env()]))
    app.config.from_object(config_class)

    # Override config with optional settings file
    app.config.from_envvar('FLASK_SETTINGS_FILE', silent=True)

    extensions.init_app(app)
    app.logger.debug('Extensions initialized.')

    with app.app_context():  # this allows to get access to config parameters
        views.init_app(app)
        app.logger.debug('Views initialized.')

    if app.config.get('MAINTENANCE_MODE'):
        app.logger.info('BEMServer in maintenance mode.')
    else:
        app.logger.info('BEMServer started. Ready to rock.')

    # Initialize Flask-Migrate
    Migrate(app, db)

    return app
