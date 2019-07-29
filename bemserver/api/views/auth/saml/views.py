"""Api SAML auth module views."""

from flask import (
    request, make_response, session, redirect, jsonify, current_app)
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from .. import bp as api
from .schemas import SSOQueryArgsSchema, SSOLoginSchemaView
from ..schemas import IdentitySchemaView

from ....extensions.rest_api import abort
from ....extensions.rest_api.doc_responses import build_responses
from ....extensions.auth.saml import prepare_flask_request, init_saml_auth


@api.route('/saml/metadata')
@api.doc(
    summary='SAML authentication: platform metadata',
    description=(
        'This endpoint returns the service provider (core platform) metadata,'
        'which should be added to the Identity Provider (IDP) database.'),
    produces=('application/xml', 'application/json',),
    responses=build_responses([200, 404, 500])
)
def get_metadata():
    """Return the metadata of platform core api (Service Provider)."""
    req = prepare_flask_request(request)
    sauth = init_saml_auth(req)
    saml_settings = sauth.get_settings()
    metadata = saml_settings.get_sp_metadata()

    # verify metadata and throw errors
    errors = saml_settings.validate_metadata(metadata)
    if len(errors) > 0:
        current_app.logger.error(sauth.get_last_error_reason())
        current_app.logger.error('Request details: %s', req)
        abort(500, message=', '.join(errors))

    # no errors, send metadata (XML format)
    resp = make_response(metadata, 200)
    resp.headers['Content-Type'] = 'application/xml'
    return resp


@api.route('/saml/sso')
@api.doc(
    summary='SAML authentication: SSO login',
    description=(
        'This endpoint must be called by a "web browser" based client to'
        ' verify that a user is authenticated and, if not, propose to redirect'
        ' to login form when not.'),
    responses=build_responses(
        [200, 401, 404, 500], schemas={
            200: IdentitySchemaView, 401: SSOLoginSchemaView})
)
@api.arguments(SSOQueryArgsSchema, location='query')
def sso(args):
    """Log in redirection, through SAML server."""
    # If already logged in don't initiate saml process
    if ('identity' in session and
            'saml_name_id' in session and 'saml_session_idx' in session):
        return jsonify(session['identity']), 200

    req = prepare_flask_request(request)
    sauth = init_saml_auth(req)

    # redirect to a custom RelayState, if any
    relay_state = args['relay_state']
    # 401 status code to signify that authentication should be done
    return jsonify({'login_url': sauth.login(return_to=relay_state)}), 401


@api.route('/saml/acs', methods=['POST'])
@api.doc(
    summary='SAML authentication: ACS callback',
    description=(
        'This endpoint is requested by SAML server as a callback, when a user'
        ' passes successfully through login form (he is authenticated).'),
    responses=build_responses([200, 302, 401, 404, 500])
)
def acs_after_login():
    """Assertion Consumer Service, IDP response after log in."""
    req = prepare_flask_request(request)
    sauth = init_saml_auth(req)
    sauth.process_response()

    # Retrieves possible validation errors
    errors = sauth.get_errors()
    if errors is not None and len(errors) > 0:
        current_app.logger.error(sauth.get_last_error_reason())
        current_app.logger.error('Request details: %s', req)
        abort(500, message=', '.join(errors))

    if not sauth.is_authenticated():
        abort(401, message='Not authenticated!')

    saml_userdata = sauth.get_attributes()
    # build identity and store to session
    user_uid = saml_userdata['uid']
    # XXX: strangely, saml_userdata['uid'] is a list...
    if isinstance(user_uid, list):
        if len(user_uid) == 1:
            user_uid = user_uid[0]
        else:
            abort(500, message='Unexpected response of Identity Provider!')
    session['identity'] = {
        'uid': user_uid,
        'roles': saml_userdata['roles'],
        'type': 'user'
    }
    # store some saml info too
    session['saml_name_id'] = sauth.get_nameid()
    session['saml_session_idx'] = sauth.get_session_index()

    # redirect to a custom RelayState, if any
    relay_state = req['post_data'].get('RelayState')
    if (relay_state is not None and
            OneLogin_Saml2_Utils.get_self_url(req) != relay_state):
        return redirect(sauth.redirect_to(relay_state))  # 302

    return jsonify(session['identity']), 200


@api.route('/saml/slo')
@api.doc(
    summary='SAML authentication: SLO logout',
    description=(
        'This endpoint can be called to disconnect a user (his cookie session'
        ' will be destroyed).'),
    responses=build_responses([302, 404, 500])
)
@api.arguments(SSOQueryArgsSchema, location='query')
def logout(args):
    """Log out redirection, through SAML."""
    req = prepare_flask_request(request)
    sauth = init_saml_auth(req)

    name_id = session.get('saml_name_id')
    session_index = session.get('saml_session_idx')
    # redirect to a custom RelayState, if any
    relay_state = args['relay_state']
    # redirection 302
    return redirect(sauth.logout(
        name_id=name_id, session_index=session_index, return_to=relay_state))


@api.route('/saml/sls')
@api.doc(
    summary='SAML authentication: SLS callback',
    description=(
        'This endpoint is requested by SAML server as a callback, when a user'
        ' has been logged out (user is not authenticated anymore).'),
    responses=build_responses([200, 302, 404, 500])
)
def after_logout():
    """IDP response after log out."""
    req = prepare_flask_request(request)
    sauth = init_saml_auth(req)

    # Obtain session clear callback
    delete_session_callback = lambda: session.clear()
    # Process the Logout Request & Logout Response
    url = sauth.process_slo(delete_session_cb=delete_session_callback)

    # Retrieves possible validation errors
    errors = sauth.get_errors()
    if len(errors) > 0:
        current_app.logger.error(sauth.get_last_error_reason())
        current_app.logger.error('Request details: %s', req)
        abort(500, message=', '.join(errors))

    if url is not None:
        return redirect(url)  # 302

    return jsonify({'message': 'Logged out!'}), 200
