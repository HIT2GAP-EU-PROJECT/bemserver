"""Api auth module views."""

from flask import current_app

from . import bp as api
from .schemas import AuthModesSchemaView

from ...extensions.rest_api.doc_responses import build_responses


@api.route('/modes')
@api.doc(
    summary='Authentication available modes endpoint',
    responses=build_responses([200, 500])
)
@api.response(AuthModesSchemaView, disable_etag=True)
def get_available_auth_mode():
    """Get available authentication modes."""
    auth_modes = []
    if current_app.config.get('AUTH_JWT_ENABLED'):
        auth_modes.append('JWT')
    if current_app.config.get('AUTH_CERTIFICATE_ENABLED'):
        auth_modes.append('CERTIFICATE')
    if current_app.config.get('AUTH_SAML_ENABLED'):
        auth_modes.append('SAML')
    return {'auth_modes': auth_modes}
