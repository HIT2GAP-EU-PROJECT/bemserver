"""Relational database extension"""

from h2g_platform_core.database.relational import db


class SqlDatabaseDoesNotExistError(OSError):
    """Specified SQL database does not exist"""


def init_app(app):
    """Initialize relational database extension"""

    # SQL
    db.init_app(app)
