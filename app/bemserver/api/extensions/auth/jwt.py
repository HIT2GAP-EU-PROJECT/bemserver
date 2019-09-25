"""JSON Web Token authentication extension."""

import datetime as dt
from functools import wraps

from flask_jwt_simple import (
    JWTManager,
    create_jwt as auth_jwt_create_token,  # noqa
    get_jwt_identity as auth_jwt_get_identity  # noqa
)
from flask_jwt_simple.view_decorators import (
    _decode_jwt_from_headers, ctx_stack)
from werkzeug.exceptions import Unauthorized, UnprocessableEntity
from flask import current_app

from bemserver.api.extensions.rest_api import rest_api
from ..database.security import _verify_roles


def init_app(app):
    """Initialize JWT authentication mode."""
    # set default config
    app.config.setdefault('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config.setdefault('AUTH_JWT_REALM', 'Login required')
    # JWT_EXPIRES only accepts 'timedelta', AUTH_JWT_EXPIRES also accepts 'int'
    jwt_expires = app.config.get('AUTH_JWT_EXPIRES')
    if jwt_expires is not None:
        if not isinstance(jwt_expires, dt.timedelta):
            jwt_expires = dt.timedelta(seconds=jwt_expires)
        app.config.setdefault('JWT_EXPIRES', jwt_expires)

    jwt_manager = JWTManager()
    jwt_manager.init_app(app)

    # because of the '_set_error_handler_callbacks' of flask_jwt_simple,
    #  we have to override some exceptions callbacks to manually call our
    # handle_http_exception with an instanciated werkzeug HTTPException.
    jwt_manager.unauthorized_loader(_unauthorized_callback)
    jwt_manager.expired_token_loader(_expired_token_callback)
    jwt_manager.invalid_token_loader(_invalid_token_callback)


def _unauthorized_callback(error_string):
    """When a protected endpoint is accessed without a JWT, throw a 401 status
    response (including an error string explaining why this is unauthorized).

    :param error_string: String indicating why this request is unauthorized.
    """
    exc = Unauthorized()
    exc.data = {
        'message': (
            'Access denied, authentication required: {}'.format(error_string)),
        'headers': {
            'WWW-Authenticate': '{} realm="{}"'.format(
                current_app.config.get('JWT_HEADER_TYPE'),
                current_app.config.get('AUTH_JWT_REALM'))
        },
    }
    return rest_api.handle_http_exception(exc)


def _expired_token_callback():
    """When an expired token attempts to access a protected endpoint, throw a
    401 status response.
    """
    exc = Unauthorized()
    exc.data = {
        'message': 'Access denied, token has expired!',
        'headers': {
            'WWW-Authenticate': '{} realm="{}"'.format(
                current_app.config.get('JWT_HEADER_TYPE'),
                current_app.config.get('AUTH_JWT_REALM'))
        },
    }
    return rest_api.handle_http_exception(exc)


def _invalid_token_callback(error_string):
    """When an invalid token attempts to access a protected endpoint, throw a
    422 status code response

    :param error_string: String indicating why the token is invalid.
    """
    exc = UnprocessableEntity()
    exc.data = {'message': error_string}
    return rest_api.handle_http_exception(exc)


def auth_jwt_required(*, roles=None):
    """
    Ensure that the requester has a valid JWT before calling the actual view.
    If authentication is disabled, func result is returned.

    :param list|tuple roles: (optional, default None)
        A list of valid roles required to execute func.
        If None, no specific role is required (func is open to all roles).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            is_auth_enabled = (
                current_app.config['AUTHENTICATION_ENABLED']
                or current_app.config['AUTHENTICATION_DEMO_ENABLED'])

            if is_auth_enabled and current_app.config['AUTH_JWT_ENABLED']:
                # verify access token
                jwt_data = _decode_jwt_from_headers()
                ctx_stack.top.jwt = jwt_data
                # before executing func, check authenticated user's roles
                _verify_roles(jwt_data['sub'], roles)

            # and finally get func result
            return func(*args, **kwargs)
        return wrapper
    return decorator
