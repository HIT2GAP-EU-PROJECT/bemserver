"""Custom query parameters"""

import marshmallow as ma

from bemserver.database import SORT_ASCENDING, SORT_DESCENDING


class SortQueryField(ma.fields.String):
    """Loads sort query string into a tuple sort query

    "field1,-field2" is deserialized into
    [(field1, SORT_ASCENDING), (field2, SORT_DESCENDING)]
    """

    @staticmethod
    def get_direction(item):
        """Translate '+field' or 'field' into (field, SORT_ASCENDING),
        '-field' into (field, SORT_DESCENDING)
        """
        if item.startswith('-'):
            return (item[1:], SORT_DESCENDING)
        elif item.startswith('+'):
            return (item[1:], SORT_ASCENDING)
        else:
            return (item, SORT_ASCENDING)

    def _deserialize(self, value, attr, data):
        sort_query_str = super()._deserialize(value, attr, data)
        sort_strings = sort_query_str.split(',')
        return [self.get_direction(item) for item in sort_strings]

    def _serialize(self, value, attr, obj):
        # We don't need serialization
        raise NotImplementedError


class SortQueryArgsSchema(ma.Schema):
    """Sort get query parameters schema"""

    sort = SortQueryField(
        description='Sort parameters'
    )
