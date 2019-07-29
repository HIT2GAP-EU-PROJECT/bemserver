"""Database accessor

Override database accessor to abort gracefully on error.
"""

import marshmallow as ma

from bemserver.database import dbaccessor as dba
from bemserver.database.exceptions import ItemNotFoundError, ItemError
from bemserver.api.extensions.rest_api import abort


class DBAccessor(dba.DBAccessor):

    def get_item_by_id(self, item_cls, item_id, *, do_abort=True):
        try:
            return super().get_item_by_id(item_cls, item_id)
        except ItemNotFoundError:
            if do_abort:
                abort(404)
        return None

    def get_list(self, item_cls, sieve=None, sort=None):
        try:
            return super().get_list(item_cls, sieve=sieve, sort=sort)
        except ItemNotFoundError:
            abort(404)

    def create(self, item, **kwargs):
        try:
            return super().create(item, **kwargs)
        except ma.ValidationError as exc:
            abort(422, errors=exc.messages)

    def update(self, item, **kwargs):
        try:
            return super().update(item, **kwargs)
        except ma.ValidationError as exc:
            abort(422, errors=exc.messages)

    def delete(self, item, **kwargs):
        try:
            return super().delete(item, **kwargs)
        except ma.ValidationError as exc:
            abort(422, errors=exc.messages)

    def get_parent(self, item_cls, item_id):
        try:
            return super().get_parent(item_cls, item_id)
        except ItemError:
            abort(404)

    def get_parent_many_classes(self, item_clss, item_id):
        for item_cls in item_clss:
            try:
                parent_id = self.get_parent(item_cls, item_id)
                return parent_id
            except Exception:
                continue
        abort(404)
