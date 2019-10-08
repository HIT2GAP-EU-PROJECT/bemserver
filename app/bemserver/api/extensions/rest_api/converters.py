"""Flask URL parameter converters"""

import uuid
import re

from werkzeug.routing import BaseConverter
from flask import abort


# The uuid.UUID() constructor accepts various formats, so use a strict
# regular expression to keep urls unique.
UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


# Custom converters
# https://exploreflask.com/views.html#custom-converters
# https://github.com/wbolster/flask-uuid/blob/master/flask_uuid.py
class UUIDConverter(BaseConverter):
    """
    UUID converter for the Werkzeug routing system.
    """

    def __init__(self, map_value, strict=True):
        super(UUIDConverter, self).__init__(map_value)
        self.strict = strict

    def to_python(self, value):
        if self.strict and not UUID_RE.match(value):
            abort(400)

        try:
            return uuid.UUID(value)
        except ValueError:
            abort(400)

    def to_url(self, value):
        return str(value)
