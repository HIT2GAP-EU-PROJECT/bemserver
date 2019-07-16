"""Api authentication module initialization."""

from ...extensions.rest_api import rest_api, Blueprint


_DESCRIPTION = """Some resources of the platform core API are protected
and require authentication to be consumed.

The access to those private endpoints is made in 2 steps:

1. Obtain a session cookie (or an access token, depending on the
authentication method used) by identifying a user through the appropriate
authentication endpoint (see below, for example `/auth/cert` if authenticating
with a certificate).

2. Pass this cookie/token in headers while requesting each private endpoint.

## USER ACCOUNTS

User accounts are divided in 2 categories, each having its dedicated
authentication mode:

* **SAML** is used for **human** users: anyone connected to the platform portal
through his web browser.

* **certificates** are used for **machine**, typically 'background' modules
such as the timeseries cleaning module.

## PERMISSIONS: ROLES & SCOPE

Permissions are defined by roles associated to each user account. A user can
cumulate roles.

A site scope can also be specified to restrict the privileges for a user to a
specific site. It is a list of site names, or '*' to grant privileges for all
sites.

For example, access to a timeseries is limited by the user's capability to
access the site where the timeseries is located.

The platform core API currently accepts 4 roles, each role providing abilities
on platform API endpoints:

role (user type)                                                                          | data model (sites, buildings, ...) | events | timeseries | occupants data |
----------------------------------------------------------------------------------------- | ---------------------------------- | ------ | ---------- | -------------- |
**chuck** (human), a.k.a. 'root', can do anything, anywhere, anytime                      |                 RW                 |   RW   |     RW     |       RW       |
**building_manager** (human), site administrator (energy manager, building owner...)      |                 RW                 |   R    |     R      |       R        |
**module_data_provider** (machine), background service that acquire timeseries            |                                    |        |     RW     |                |
**module_data_processor** (machine), background service that compute events or timeseries |                 R                  |   RW   |     RW     |       R        |

*(RW: read/write, R: read only)*

## AUTHENTICATION METHODS

### SAML

In SAML terminology, the platform core API is a Service Provider (SP). Its role
is to communicate with the SAML server to deliver an assertion and identify a
user.

Each web-based external module should authenticate through the web browser
using the platform core API in accordance with the
[SAML protocol](https://developers.onelogin.com/saml).
Authentication endpoints to call are `/auth/saml/sso` to login and
`/auth/saml/slo` to logout.

Remember that an Identity Provider (IDP) must know each SP that requests him,
by addind the SP's metadata to its database.

### CERTIFICATE

Certificates are generated and delivered by the platform core administrator.
The only requirement is that the module owner describes his app, in order
to define a unique module name for the certificate.
The certificate can be used from anywhere but authenticates only one module.

### DEMO

Once authenticated, the access to private content can be tested by requesting
`/auth/demo/private` endpoint.

You can also verify roles requirement through:
- `/auth/demo/private/roles/0` for *building_manager* role only
- `/auth/demo/private/roles/1` for *module_data_provider* and
*module_data_processor* roles
"""


bp = Blueprint('auth', __name__, url_prefix='/auth', description=_DESCRIPTION)


def init_app(app):
    """Initialize application with module"""

    if app.config['AUTH_JWT_ENABLED']:
        from . import jwt
        jwt.init_app(app)

    if app.config['AUTH_CERTIFICATE_ENABLED']:
        from . import tlsclient
        tlsclient.init_app(app)

    if app.config['AUTH_SAML_ENABLED']:
        from . import saml
        saml.init_app(app)

    if app.config['AUTHENTICATION_DEMO_ENABLED']:
        from . import demo_views  # noqa

    from . import views  # noqa

    rest_api.register_blueprint(bp)
