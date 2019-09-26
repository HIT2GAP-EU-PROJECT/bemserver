"""Bonus marshmallow fields"""

from dateutil.tz import tzutc

import marshmallow as ma


class StrictDateTime(ma.fields.DateTime):
    """
    Marshmallow DateTime field with extra parameter to control
    whether dates should be loaded as tz_aware or not

    Borrowed from umongo
    """

    def __init__(self, *args, load_as_tz_aware=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_as_tz_aware = load_as_tz_aware

    def _deserialize(self, value, attr, data):
        date = super()._deserialize(value, attr, data)
        return self._set_tz_awareness(date)

    def _set_tz_awareness(self, date):
        if self.load_as_tz_aware:
            # If datetime is TZ naive, set UTC timezone
            if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
                date = date.replace(tzinfo=tzutc())
        else:
            # If datetime is TZ aware, convert it to UTC and remove TZ info
            if (date.tzinfo is not None
                    and date.tzinfo.utcoffset(date) is not None):
                date = date.astimezone(tzutc())
            date = date.replace(tzinfo=None)
        return date


class StringList(ma.fields.List):
    """Marshmallow field storing a list of strings in a single string

    Each string is quoted to help potential string queries: assuming strings
    can not contain quotes, searching for "mystring" guarantees exact matches.
    """
    def __init__(self, **kwargs):
        super().__init__(ma.fields.String(), **kwargs)

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        if value == '':
            return []
        return [item.rstrip('"').lstrip('"') for item in value.split(';')]

    def _deserialize(self, value, attr, data):
        res = super()._deserialize(value, attr, data)
        items_with_semicolon = [i for i in res if ';' in i]
        if items_with_semicolon:
            raise ma.ValidationError('Character ";" not allowed.')
        return ';'.join(['"{}"'.format(item) for item in res])
