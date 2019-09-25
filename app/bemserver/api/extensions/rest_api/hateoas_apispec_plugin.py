"""
apispec helpers to add hateoas type fields in doc
"""

import marshmallow as ma

from flask_marshmallow.fields import Hyperlinks

from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.ext.marshmallow.common import (
    resolve_schema_cls, resolve_schema_instance)
from apispec.exceptions import PluginMethodNotImplementedError


def _rapply(schema, func, *args, **kwargs):
    """Apply a function to all values in a dictionary or list of dictionaries,
    recursively.
    """
    if isinstance(schema, (tuple, list)):
        return [_rapply(each, func, *args, **kwargs) for each in schema]
    elif isinstance(schema, dict):
        return {
            key: (_rapply(value, func, *args, **kwargs)
                  if isinstance(value, ma.fields.Field)
                  else {
                      'type': 'object',
                      'properties': _rapply(value, func, *args, **kwargs)
                  })
            for key, value in schema.items()
        }
    else:
        return func(schema, *args, **kwargs)


class HateoasPlugin(MarshmallowPlugin):

    def __init__(self):
        super().__init__()
        self.references = {}

    def definition_helper(self, name, schema, **kwargs):
        """Definition helper that allows using a marshmallow
        :class:`Schema <marshmallow.Schema>` to provide OpenAPI metadata.

        :param str name: Name to use for definition.
        :param type|Schema schema: A marshmallow Schema class or instance.
        """
        schema_cls = resolve_schema_cls(schema)
        schema_instance = resolve_schema_instance(schema)

        # Store registered refs, keyed by Schema class
        self.references[schema_cls] = name

        if hasattr(schema_instance, 'fields'):
            fields = schema_instance.fields
        elif hasattr(schema_instance, '_declared_fields'):
            fields = schema_instance._declared_fields
        else:
            raise ValueError(
                "{0!r} doesn't have either `fields` or `_declared_fields`"
                .format(schema_instance)
            )

        ret = super().definition_helper(name, schema_instance, **kwargs)

        for field_name, field_obj in fields.items():
            if isinstance(field_obj, Hyperlinks):
                ret['properties'][field_name]['properties'] = _rapply(
                    field_obj.schema, self.openapi.field2property, name=name)

        return ret

    def path_helper(self, *args, **kwargs):
        """We don't need apispec's MarshmallowPlugin path helper"""
        raise PluginMethodNotImplementedError

    def operation_helper(self, *args, **kwargs):
        """We don't need apispec's MarshmallowPlugin operation helper"""
        raise PluginMethodNotImplementedError
