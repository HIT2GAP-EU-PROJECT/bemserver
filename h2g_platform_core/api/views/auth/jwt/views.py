"""Api auth module views."""

from flask import session

from .. import bp as api
from .schemas import JWTLoginSchemaView, JWTLoginBodySchema

from ...occupant_users.auth_occupant_user import authenticate_occupant_user

from ....extensions.rest_api import abort
from ....extensions.rest_api.doc_responses import build_responses
from ....extensions.auth.jwt import auth_jwt_create_token


@api.route('/jwt', methods=['POST'])
@api.doc(
    summary='JSON Web Token authentication endpoint',
    responses=build_responses([200, 401, 422, 500])
)
@api.arguments(JWTLoginBodySchema)
@api.response(JWTLoginSchemaView, disable_etag=True)
def auth_jwt_login(data):
    """Login an user through JSON Web Token authentication."""
    occ_user = authenticate_occupant_user(data)
    if occ_user is None:
        abort(401, message='Invalid credentials!')
    # occupant user authentication identity
    identity = occ_user.get_identity()
    # set a server cookie with user authentication identity
    session['identity'] = identity
    # Generate JWT token
    access_token = auth_jwt_create_token(identity=identity)
    return {'access_token': access_token}
