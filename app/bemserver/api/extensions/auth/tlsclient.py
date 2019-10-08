"""TLS (certificate) authentication extension."""

from flask import current_app, request
from werkzeug.exceptions import UnprocessableEntity


def init_app(app):
    """Initialize certificate authentication mode."""
    tls_client = TLSClient()
    tls_client.init_app(app)


class TLSClient():
    """Certificate authentication."""

    def __init__(self, app=None):
        """Create the TLSClient instance. You can either pass a flask
        application in directly here to register this extension with the
        flask app, or call init_app after creating this object.

        :param app: A flask application.
        """
        # Register this extension with the flask app now (if it is provided)
        if app is not None:
            self.init_app(app)

    @staticmethod
    def _set_default_config_options(app):
        """Sets the default configuration options used by this extension."""
        # Options for certificate location (SSL_CLIENT_S_DN header)
        app.config.setdefault('AUTH_CERT_REQUEST_ENV', 'HTTP_SSL_CLIENT_S_DN')
        # certificate attribute key name to retrieve identity unique name
        app.config.setdefault('AUTH_CERT_ATTR_NAME', 'CN')
        # www-authenticate header value
        app.config.setdefault('AUTH_CERT_WWW_AUTHENTICATE',
                              'transport mode="tls-client-certificate"')

    def init_app(self, app):
        """Register this extension with the flask app.

        :param app: A flask application.
        """
        # Save this so we can use it later in the extension
        if not hasattr(app, 'extensions'):   # pragma: no cover
            app.extensions = {}
        app.extensions['flask-tlsclient '] = self

        # Set all the default configurations for this extension
        self._set_default_config_options(app)


def build_www_auth_header():
    """Return WWW-Authenticate header."""
    return {
        'WWW-Authenticate': current_app.config['AUTH_CERT_WWW_AUTHENTICATE']}


def _build_exception_data(message=''):
    return {'message': message, 'headers': build_www_auth_header()}


def auth_cert_get_uid():
    """Get the unique name extracted from the authentication certificate.

    :returns str: The identity unique name.
    """
    # decode certificate from current request headers
    header_name = current_app.config['AUTH_CERT_REQUEST_ENV']
    attr_name = current_app.config['AUTH_CERT_ATTR_NAME']

    # Verify certificate auth header is present
    # The certificate was accepted by the Certification Authority declared
    #  in Apache virtual host config file.
    s_dn = request.environ.get(header_name)
    if s_dn is None or s_dn == '(null)':
        exc = UnprocessableEntity()
        exc.data = _build_exception_data(
            'Missing "{}" header'.format(header_name))
        raise exc

    # dispatch certificate data in a dict
    try:
        cert_attrs = dict([x.split('=') for x in s_dn.split(',')])
    except ValueError:
        exc = UnprocessableEntity()
        exc.data = _build_exception_data('Invalid certificate!')
        raise exc
    # Get identity name for certificate attributes
    try:
        name = cert_attrs[attr_name]
    except KeyError:
        exc = UnprocessableEntity()
        exc.data = _build_exception_data(
            'Invalid certificate: missing "{}" attribute!'.format(attr_name))
        raise exc

    # Return identity unique name
    return name
