"""Database extension"""

from .accessor import DBAccessor
from bemserver.database import init_handlers


db_accessor = DBAccessor()


def init_app(app):
    """Initialize ontology manager"""

    base_url = app.config['ONTOLOGY_BASE_URL']
    db_accessor.set_handler(init_handlers(base_url))
