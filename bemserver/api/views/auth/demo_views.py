"""Api auth DEMO module views."""

from . import bp as api

from ...extensions.rest_api.doc_responses import build_responses
from ...extensions.auth import auth_required, get_identity


@api.route('/demo/private')
@auth_required(with_perm=False)
@api.doc(
    summary='DEMO: access to private content, no role required',
    description=(
        'This endpoint aims to test the access to private content using'
        ' authentication data (cookie or token).'),
    responses=build_responses([200, 404, 422, 500])
)
@api.response(disable_etag=True)
def auth_demo_private():
    """DEMO endpoint protected with authentication."""
    return _private_access()


@api.route('/demo/private/roles/0')
@auth_required(roles=['building_manager'], with_perm=False)
@api.doc(
    summary='DEMO: access to private content, roles required (case #0)',
    description=(
        'This endpoint aims to test the access to private content using'
        ' authentication data (cookie or token), roles are required.'),
    responses=build_responses([200, 400, 404, 422, 500])
)
@api.response(disable_etag=True)
def auth_demo_private_roles_0():
    """DEMO endpoint protected with authentication and roles required."""
    return _private_access()


@api.route('/demo/private/roles/1')
@auth_required(
    roles=['module_data_provider', 'module_data_processor'], with_perm=False)
@api.doc(
    summary='DEMO: access to private content, roles required (case #1)',
    description=(
        'This endpoint aims to test the access to private content using'
        ' authentication data (cookie or token), roles are required.'),
    responses=build_responses([200, 400, 404, 422, 500])
)
@api.response(disable_etag=True)
def auth_demo_private_roles_1():
    """DEMO endpoint protected with authentication and roles required."""
    return _private_access()


def _private_access():
    identity = get_identity()
    if identity is None:
        # this case should never happen...
        return 'Hello anonymous, access authorized!'
    return 'Hello {}, access granted as {}!'.format(
        identity['uid'], identity['roles'])
