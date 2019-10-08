"""Authentication extensions."""

from functools import wraps

from flask import (
    current_app, session, request, has_request_context, has_app_context)

from . import jwt
from . import tlsclient
from . import saml

from ..rest_api import abort
from ..rest_api.doc_responses import build_responses
from ..database.security import get_security_manager, _verify_roles


def init_app(app):
    """Initialize authentication modes."""
    # set authentication modes default enabled value
    jwt_auth = app.config.setdefault('AUTH_JWT_ENABLED', False)
    cert_auth = app.config.setdefault('AUTH_CERTIFICATE_ENABLED', False)
    saml_auth = app.config.setdefault('AUTH_SAML_ENABLED', False)

    # initialize JWT authentication
    if jwt_auth:
        jwt.init_app(app)

    # initialize certificate authentication
    if cert_auth:
        tlsclient.init_app(app)

    # initialize SAML authentication
    if saml_auth:
        saml.init_app(app)

    # warn if no authentication mode is enabled
    if not any((jwt_auth, cert_auth, saml_auth)):
        app.logger.warning('Authentication module is enabled while all '
                           'authentication methods are disabled.')


def auth_required(*, roles=None, with_perm=True):
    """Ensure that the requester has a valid cookie session before calling
    the actual view. If authentication is disabled, func result is returned.

    ..Note:
        Cookie session can be replaced by a valid JWT access token.

    :param list|tuple roles: (optional, default None)
        A list of valid roles required to execute func.
        If None, no specific role is required (func is open to all roles).
    :param bool with_perm: (optional, default True)
        True if resources are protected with permissions.
        (only for documentation purposes)
    """
    def _update_apidoc(func):
        # hack to update endpoint description and responses in APIspec doc
        # /!\ to make things work decently, call @auth_required after @api.doc

        # ensure _apidoc exists as a dict-type func attribute
        func._apidoc = getattr(func, '_apidoc', {})

        # first, we want to show that authentication is required
        auth_desc = '**[Authentication required]**'
        # and we also want to show which roles are required, if any
        if roles is not None and len(roles) > 0:
            # make it beautiful to our sensitive eyes...
            if len(roles) <= 1:
                auth_desc = '{}, restricted to *{}* role.'.format(
                    auth_desc, roles[-1])
            else:
                auth_roles = ['*{}*'.format(role) for role in roles]
                auth_desc = '{}, restricted to {} roles.'.format(
                    auth_desc, ' and '.join(
                        [', '.join(auth_roles[:-1]), auth_roles[-1]]))
        if with_perm:
            # show permissions scope (which are always on site)
            auth_desc = '{}\n\n**[Permissions scope]** site'.format(auth_desc)
        # finally update description with new insertions on top
        desc = func._apidoc.get('description', '')
        func._apidoc['description'] = '{}{}'.format(
            auth_desc, '\n\n{}'.format(desc) if len(desc) > 0 else desc)

        # then, add authentication/permissions responses status codes
        func._apidoc.get('responses', {}).update(build_responses([401, 403]))

    def decorator(func):

        if is_auth_enabled(func_name=func.__name__):
            _update_apidoc(func)

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not is_auth_enabled():
                return func(*args, **kwargs)

            # authentication enabled
            app_conf = current_app.config
            is_auth_jwt = app_conf['AUTH_JWT_ENABLED']
            is_auth_cert = app_conf['AUTH_CERTIFICATE_ENABLED']
            is_auth_saml = app_conf['AUTH_SAML_ENABLED']

            func_result = None
            # try to get identity data from session cookie
            identity = session.get('identity')
            # verify authentication through session cookie
            if identity is not None:
                # first, verify that user has required roles
                _verify_roles(identity, roles)
                # function can be processed
                func_result = func(*args, **kwargs)
            # maybe JWT authentication is used (access token)
            elif is_auth_jwt:
                # try to process function (or abort 403/404)
                func_result = jwt.auth_jwt_required(
                    roles=roles)(func)(*args, **kwargs)
                # get identity
                identity = jwt.auth_jwt_get_identity()

            # it seems that authentication could not be done
            if identity is None:
                # /!\ at this point, the jwt 401 case is already processed
                headers = {}
                if is_auth_cert:
                    headers.update(tlsclient.build_www_auth_header())
                if is_auth_saml:
                    headers.update(saml.build_www_auth_header())
                abort(401, headers=headers)

            return func_result

        return wrapper
    return decorator


def get_identity():
    """Return authenticated identity, whatever the authentication mode.

    :return dict: Identity data.
    """
    # get identity from session cookie
    identity = session.get('identity')

    # when authentication identity is not cookie style...
    if (identity is None and has_app_context() and
            current_app.config['AUTH_JWT_ENABLED']):
        identity = jwt.auth_jwt_get_identity()

    return identity


def get_user_account():
    """Return authenticated user account.

    :return UserAccount: Authenticated user account.
    """
    if not is_auth_enabled():
        return None

    # get user account data
    identity = get_identity()
    if identity is None:
        abort(401, message='User could not be identified!')
    security_mgr = get_security_manager()
    return security_mgr.get(identity['uid'])


def is_auth_enabled(func_name=None):
    """Is authentication enabled? (at least one method is enabled)

    :param str func_name: (optional, default None)
        When request context is not found, func_name is used to verfify that
        current endpoint url is auth demo or not (apispec documentation case).
    """
    # auth enabled or auth demo enabled and current url is auth demo
    #  and at least one auth method enabled
    if not has_app_context():
        return False

    is_url_demo = False
    auth_demo_endpoint = current_app.config['AUTHENTICATION_DEMO_ENDPOINT']
    if has_request_context():
        is_url_demo = auth_demo_endpoint in request.url
    elif func_name is not None:
        is_url_demo = auth_demo_endpoint[1:].replace(
            '/', '_') in func_name.lower()

    return (
        (current_app.config['AUTHENTICATION_ENABLED'] or (
            # auth demo case
            current_app.config['AUTHENTICATION_DEMO_ENABLED'] and is_url_demo))
        and (
            # is at least one authentication mode active?
            current_app.config['AUTH_JWT_ENABLED'] or
            current_app.config['AUTH_CERTIFICATE_ENABLED'] or
            current_app.config['AUTH_SAML_ENABLED']))


def verify_scope(*, sites=None):
    """Verify user's permissions on site. Abort 403 if not authorized.

    :param list sites: (optional, default None)
        A list of site unique IDs (names) for which user access is verified.
    """
    if is_auth_enabled() and sites is not None:
        # verify authenticated user's scopes
        uacc = get_user_account()
        if not uacc.verify_scope(sites=sites):
            abort(403, message='User unauthorized on {} sites!'.format(sites))
