"""Flask app config file"""

import os
import datetime as dt
from pathlib import Path


APPLICATION_PATH = Path(__file__).parent


class Config():
    """Base flask app config class"""

    # 0. app state settings
    TESTING = False
    # 0.1. session settings
    # use cookies only on HTTPS requests
    SESSION_COOKIE_SECURE = True
    # cookie lifetime to 1 hour
    PERMANENT_SESSION_LIFETIME = dt.timedelta(hours=1)

    # 1. API settings
    # 1.1. general settings
    PREFERRED_URL_SCHEME = 'http'
    API_VERSION = '0.1'
    # 1.2. API documentation settings
    OPENAPI_VERSION = '2.0'
    OPENAPI_URL_PREFIX = '/api-docs/'
    OPENAPI_JSON_PATH = 'api-docs.json'
    OPENAPI_REDOC_PATH = 'redoc'
    OPENAPI_REDOC_VERSION = 'next'
    # 1.3. etag feature
    ETAG_ENABLED = True
    # 1.5. upload settings
    MAX_CONTENT_LENGTH = 250 * 1024 * 1024  # 250 Mo
    # 1.7 data model / events API disabling
    DATA_MODEL_API_DISABLED = False
    OCCUPANTS_API_DISABLED = False
    IFC_API_DISABLED = False
    EVENTS_API_DISABLED = False

    # 2. logging
    # Valid record names are standard ones
    # https://docs.python.org/3.5/library/logging.html#logrecord-attributes
    # to which we added "url", "method" and "remote_addr"
    LOGGER_FORMAT = (
        '%(asctime)s | %(levelname)-8s | '
        '%(remote_addr)-15s | %(method)s | %(url)s | '
        '%(message)s')
    LOGGER_LEVEL = 'INFO'
    LOGGER_BACKUP = 30

    # 3. storage
    # 3.1 Time Series storage
    TIMESERIES_BACKEND = 'hdfstore'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 3.2 Triple store

    # 4. maintenance
    MAINTENANCE_MODE = False

    # 5. authentication
    AUTHENTICATION_ENABLED = False
    AUTHENTICATION_DEMO_ENABLED = False
    AUTHENTICATION_DEMO_ENDPOINT = '/auth/demo/private'
    # 5.1. JWT authentication settings (occupant)
    AUTH_JWT_ENABLED = False
    # AUTH_JWT_EXPIRES also accepts a number of seconds as an int
    AUTH_JWT_EXPIRES = dt.timedelta(hours=1)
    # 5.2. certificate authentication settings
    AUTH_CERTIFICATE_ENABLED = False
    # 5.3. SAML authentication settings
    AUTH_SAML_ENABLED = False
    # Force to 1 for pre-prod with cert
    AUTH_SAML_REDIRECT_HTTPS = os.environ.get('IS_HOST_HTTPS', 1)

    # 6. concurrent requests limits
    CONCURRENT_REQUESTS_LIMITS_ENABLED = False


class ProductionConfig(Config):
    """Production mode flask app config class"""

    PREFERRED_URL_SCHEME = 'https'
    AUTHENTICATION_ENABLED = True
    AUTH_JWT_ENABLED = True
    AUTH_JWT_REALM = 'bemserver'
    AUTH_CERTIFICATE_ENABLED = True


class DevelopmentConfig(Config):
    """Development mode flask app config class"""

    SECRET_KEY = 'dummy_key'
    ETAG_ENABLED = False

    # To use in dev mode, create security dir in same dir as the repo
    #  or override SECURITY_STORAGE_DIR in a settings.cfg file
    SECURITY_STORAGE_DIR = str(APPLICATION_PATH.parents[3] / 'security')

    ONTOLOGY_BASE_URL = 'http://localhost:3030/bemserver/'
    # To use in dev mode, create hdf5 dir in same dir as the repo
    # or override TIMESERIES_BACKEND_STORAGE_DIR in a settings.cfg file
    TIMESERIES_BACKEND_STORAGE_DIR = str(APPLICATION_PATH.parents[3] / 'hdf5')
    FILE_STORAGE_DIR = str(APPLICATION_PATH.parents[3] / 'file_repo')
    # To use in dev mode, create sqlite dir in same dir as the repo
    # or override SQLALCHEMY_DATABASE_URI in a settings.cfg file
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
        str(APPLICATION_PATH.parents[3] / 'sqlite/event.db'))

    # To use in dev mode, create security/saml dir in same dir as the repo
    #  or override AUTH_SAML_DIR in a settings.cfg file
    AUTH_SAML_DIR = str(Path(SECURITY_STORAGE_DIR) / 'saml')


class TestingConfig(Config):
    """Testing mode flask app config class"""

    SECRET_KEY = 'dummy_key'
    TESTING = True
    LOGGER_DIR = '/dummy'  # Replaced in init_app fixture
    LOGGER_LEVEL = 'DEBUG'
    ONTOLOGY_BASE_URL = 'http://localhost:3030/bemserver_test/'
    ONTOLOGY_MODELS_PATH = '../../BEMOnt/models/RDF'
    TIMESERIES_BACKEND_STORAGE_DIR = '/dummy'  # Replaced in init_app fixture
    FILE_STORAGE_DIR = '/dummy'  # Replaced in init_app fixture
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
