"""Custom pagination classes"""

from flask_rest_api import Page


class SQLCursorPage(Page):
    """SQL cursor pager"""

    @property
    def item_count(self):
        return self.collection.count()
