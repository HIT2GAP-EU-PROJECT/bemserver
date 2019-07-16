"""Api anonymous occupant users module views."""

from . import bp as api

from .auth_occupant_user import authenticate_occupant_user
from .schemas import (
    OccupantAccountSchemaView,
    OccupantChangePwdRequestBodySchema)

from ...extensions.rest_api import abort
from ...extensions.rest_api.doc_responses import build_responses
from ...extensions.auth import auth_required
from ...extensions.database.security import get_security_manager
from ...extensions.database.exceptions import ItemNotFoundError


@api.route('/generate_account', methods=['POST'])
@api.doc(
    summary='Generate an account for occupation survey',
    responses=build_responses([200, 404, 422, 500])
)
@api.response(OccupantAccountSchemaView, disable_etag=True)
def occupant_generate_account():
    """Generate and return an account, to use in occupation survey"""
    # create occupant user account using security manager
    security_mgr = get_security_manager()
    occ_uacc, new_pwd = security_mgr.create_occupant()

    # clear password needed to be returned, so the user can use it later...
    return {'login_id': occ_uacc, 'password': new_pwd}


@api.route('/<string:login_id>/regenerate_pwd', methods=['POST'])
@api.doc(
    summary='Regenerate a password for an occupation survey account',
    responses=build_responses([200, 404, 422, 500])
)
@api.response(OccupantAccountSchemaView, disable_etag=True)
def occupant_regenerate_pwd(login_id):
    """Return a regenerated password for an occupation survey account
    Regeneration is allowed when not authenticated because the purpose is to
    give a fresh password when user does not remember it..."""
    # get security manager
    security_mgr = get_security_manager()
    try:
        # update occupant user account password
        new_pwd = security_mgr.update_pwd(login_id)
    except ItemNotFoundError:
        abort(404, message='User {} not found'.format(login_id))

    # clear password needed to be returned, so the user can use it later...
    return {'login_id': login_id, 'password': new_pwd}


@auth_required(roles=['anonymous_occupant'])
@api.route('/<string:login_id>/change_pwd', methods=['PUT'])
@api.doc(
    summary='Change the password for an occupation survey account',
    responses=build_responses([200, 404, 422, 500])
)
@api.arguments(OccupantChangePwdRequestBodySchema)
@api.response(OccupantAccountSchemaView, disable_etag=True)
def occupant_change_pwd(args, login_id):
    """Return a regenerated password for an occupation survey account"""
    old_pwd = args.get('password', None)
    new_pwd = args.get('new_password', None)

    # try to identify user
    payload = {'login_id': login_id, 'password': old_pwd}
    occ_uacc = authenticate_occupant_user(payload)
    if occ_uacc is None:
        abort(404, message='User {} not found'.format(login_id))

    # get security manager
    security_mgr = get_security_manager()
    try:
        # update occupant user account password
        security_mgr.update_pwd(login_id, new_pwd=new_pwd)
    except ItemNotFoundError:
        abort(404, message='User {} not found'.format(login_id))

    return {'login_id': occ_uacc.login_id}
