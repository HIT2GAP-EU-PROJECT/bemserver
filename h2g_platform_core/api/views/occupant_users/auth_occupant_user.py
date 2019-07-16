"""Occupant user authentication."""

from ...extensions.database.security import get_security_manager
from ....database.exceptions import ItemNotFoundError


def identify_occupant_user(login_id):
    """Get occupant user account.

    :param str login_id: Occupant user login ID.
    :return UserAccount: The instance of occupant user account or None.
    """
    security_mgr = get_security_manager()
    try:
        # try to get user from database
        return security_mgr.get(login_id)
    except ItemNotFoundError:
        # something went wrong, no user identified
        return None


def authenticate_occupant_user(payload):
    """Authenticate occupant user.

    :param dict payload: Authentication payload.
        Example: {'login_id': 'login', 'password': 'pwd'}
    :return UserAccount: The instance of authenticated occupant user or None.
    """
    uacc = identify_occupant_user(payload['login_id'])
    if uacc is not None:
        # ...compare his password with the one given
        password = payload['password']
        if uacc.verify_password(password):
            return uacc
    # something went wrong, no user identified
    return None
