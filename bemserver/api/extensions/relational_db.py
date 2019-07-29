"""Relational database extension"""

from bemserver.database.relational import db


class SqlDatabaseDoesNotExistError(OSError):
    """Specified SQL database does not exist"""


def init_app(app):
    """Initialize relational database extension"""

    # SQL
    db.init_app(app)
