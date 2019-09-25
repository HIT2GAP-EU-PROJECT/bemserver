"""REST api extension initialization"""

from flask_rest_api import Api
from flask_rest_api import abort, Blueprint, Page, check_etag, set_etag  # noqa

from .. import marshmallow as ext_ma
from .converters import UUIDConverter
from .hateoas import ma_hateoas
from .custom_fields import FileField
from .pagination import SQLCursorPage  # noqa
from .schemas import ErrorSchema, Float
from .hateoas_apispec_plugin import HateoasPlugin


rest_api = Api()


def init_app(app):
    """Initialize REST api"""

    hateoas_plugin = HateoasPlugin()

    rest_api.init_app(app, spec_kwargs={'plugins': (hateoas_plugin, )})
    ma_hateoas.init_app(app)

    # Register UUIDConverter in Flask and in doc
    rest_api.register_converter(UUIDConverter, 'string', 'UUID', name='uuid')

    # Register hateoas custom Marshmallow fields in doc
    rest_api.register_field(
        ext_ma.fields.StrictDateTime, 'string', 'date-time')
    rest_api.register_field(ext_ma.fields.StringList, 'array', None)
    rest_api.register_field(ma_hateoas.Hyperlinks, 'object', None)
    rest_api.register_field(ma_hateoas.URLFor, 'string', 'url')
    # Also register monkey-patched Float
    rest_api.register_field(Float, 'number', 'float')

    # Register FileField custom field in doc
    rest_api.register_field(FileField, 'file', None)

    # Register ErrorSchema definition
    rest_api.definition('Error')(ErrorSchema)
