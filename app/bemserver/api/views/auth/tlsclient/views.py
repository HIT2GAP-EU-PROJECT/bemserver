"""Api certificate auth module views."""

from flask import session

from .. import bp as api
from ..schemas import IdentitySchemaView

from ....extensions.rest_api import abort
from ....extensions.rest_api.doc_responses import build_responses
from ....extensions.auth.tlsclient import auth_cert_get_uid
from ....extensions.database.security import get_security_manager

from .....database.exceptions import ItemNotFoundError


@api.route('/cert', methods=['POST'])
@api.doc(
    summary='Certificate authentication endpoint',
    description=(
        'This endpoint must be called by a service (not a web client) to'
        ' authentify a user (of machine type).'),
    responses=build_responses([200, 404, 422, 500])
)
@api.response(IdentitySchemaView, disable_etag=True)
def auth_cert_login():
    """Endpoint to authenticate a user through a certificate."""
    # extract user unique name from certificate
    uid = auth_cert_get_uid()

    # get security manager...
    security_mgr = get_security_manager()
    try:
        # ...to search for user account using its unique name
        user_account = security_mgr.get(uid)
    except ItemNotFoundError:
        abort(404, message='User {} not found'.format(uid))

    # set a server cookie with user authentication identity
    session['identity'] = user_account.get_identity()

    return session['identity']
