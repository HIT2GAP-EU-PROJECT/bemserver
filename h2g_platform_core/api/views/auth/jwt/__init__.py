"""Api JWT authentication module initialization."""


def init_app(app):
    """Initialize application with module"""
    from . import views  # noqa
