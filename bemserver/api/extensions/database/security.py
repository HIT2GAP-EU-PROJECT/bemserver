"""Security manager extension."""

from flask import current_app

from bemserver.database.security.security_manager import (
    SecurityManager)

from ..rest_api import abort


def get_security_manager():
    """Return security manager according to application configuration."""
    # Instantiate security manager
    return SecurityManager(current_app.config.get('SECURITY_STORAGE_DIR'))


def _verify_roles(identity, req_roles):
    """Verify that user's roles are enough. Abort 403 if not.

    :param dict identity: Authenticated user identity info.
        ..Example:
            {'uid': 'user@mail.com', 'type': 'user', 'roles': ['r1', 'r2']}
    :param list req_roles: Required roles needed to execute a function.
    """
    # verify roles of authenticated user
    if req_roles is not None and len(req_roles) > 0:
        security_mgr = get_security_manager()
        if not security_mgr.has_roles(identity['uid'], req_roles):
            abort(403, message='User has not required role(s)!')
