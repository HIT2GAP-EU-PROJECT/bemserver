"""SAML authentication extension."""

import os
from urllib.parse import urlparse
from flask import current_app
from onelogin.saml2.auth import OneLogin_Saml2_Auth


def init_app(app):
    """Initialize SAML authentication mode.

    :param Flask app: Flask instance.
    """
    # set default config
    # www-authenticate header value
    app.config.setdefault('AUTH_SAML_WWW_AUTHENTICATE', 'SAML')
    # Force HTTPS use (SAML server must be protected with a certificate)
    app.config.setdefault(
        'AUTH_SAML_REDIRECT_HTTPS', os.environ.get('IS_HOST_HTTPS', 1))


def init_saml_auth(preq):
    """Return an instanciated SAML authentication object.

    :param dict preq: Prepared Flask request metadata.
    :return OneLogin_Saml2_Auth: A OneLogin_Saml2_Auth instance (SAML client).
    """
    # get SAML client config path
    saml_dirpath = current_app.config['AUTH_SAML_DIR']
    return OneLogin_Saml2_Auth(preq, custom_base_path=saml_dirpath)


def prepare_flask_request(req):
    """Return a prepared flask request for SAML authentication instance.

    :param Request req: Flask request instance.
    :returns dict: Prepared Flask request metadata (for `OneLogin_Saml2_Auth`).
    """
    url_data = urlparse(req.url)
    is_https = (req.scheme == 'https'
                # when request is not secured (HTTP only), force HTTPS
                or bool(int(current_app.config['AUTH_SAML_REDIRECT_HTTPS'])))
    return {
        'https': 'on' if is_https else 'off',
        'http_host': req.host,
        'server_port': url_data.port,
        # /!\ req.path is not enough (missing prefix added in apache config)
        'script_name': url_data.path,
        'get_data': req.args.copy(),
        'post_data': req.form.copy()
    }


def build_www_auth_header():
    """Return WWW-Authenticate header."""
    return {
        'WWW-Authenticate': current_app.config['AUTH_SAML_WWW_AUTHENTICATE']}
