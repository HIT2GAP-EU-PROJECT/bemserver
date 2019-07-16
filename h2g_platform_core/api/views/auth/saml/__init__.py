"""Api SAML authentication module initialization.

From the SAML point of view, platform api is considered as a Service Provider.
"""


def init_app(app):
    """Initialize application with module"""

    from . import views  # noqa
