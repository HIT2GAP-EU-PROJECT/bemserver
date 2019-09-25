"""Base data model"""

import abc
from uuid import UUID

import datetime as dt
import pytz

from ..tools.common import check_list_instances


class Thing(abc.ABC):
    """Thing is all model's base class"""

    @abc.abstractmethod
    def __init__(self, *, id=None):
        self.id = id
        super(Thing, self).__init__()

    def __repr__(self):
        def _get_and_format_field_value(field_name):
            value = getattr(self, field_name, None)
            if isinstance(value, str):
                value = '"{}"'.format(value)
            elif isinstance(value, dt.datetime):
                value = '"{}"'.format(value.isoformat())
            return value

        return '<{self.__class__.__name__}>({attrs})'.format(
            self=self, attrs=', '.join(['{}={}'.format(
                field_name,
                _get_and_format_field_value(field_name)
            ) for field_name in self._fields]))

    @property
    def _fields(self):
        return [a for a in dir(self)
                if a[:1] != '_' and not callable(getattr(self, a))]

    def update(self, data):
        """Update object values from datas

        Note embedded Thing objects won't be instantiated from raw dict data.
        But it is possible to pass a dict with embedded Thing objects in it.

        Note: This works like a dict update, not like a REST PUT. Values
        missing from data are not removed from self.
        """
        for key, val in data.items():
            setattr(self, key, val)

    def dump(self, exclude=(), exclude_none=True):
        """Return a dict of datas"""
        def _format_field_value(field_value):
            if isinstance(field_value, dt.datetime):
                field_value = pytz.utc.localize(field_value).isoformat()
            elif isinstance(field_value, UUID):
                field_value = str(field_value)
            return field_value

        fields = [field for field in self._fields if field not in exclude]
        result = {}
        for cur_field in fields:
            cur_value = getattr(self, cur_field, None)
            if not exclude_none or (exclude_none and cur_value is not None):
                if check_list_instances(cur_value, Thing):
                    cur_value = [
                        inner_field_value.dump(
                            exclude=exclude, exclude_none=exclude_none)
                        for inner_field_value in cur_value]
                if isinstance(cur_value, Thing):
                    cur_value = cur_value.dump(
                        exclude=exclude, exclude_none=exclude_none)
                result[cur_field] = _format_field_value(cur_value)
        return result
