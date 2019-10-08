"""Mock database"""

from operator import attrgetter

import inspect
from uuid import uuid1 as uuid_gen

from .exceptions import (
    ItemNotFoundError, ItemSaveError, ItemDeleteError)


SORT_ASCENDING = 1
SORT_DESCENDING = -1


class DatabaseMock():
    """Database mock

    Stores data in a dict (by collections) and provides data management methods
    """

    def __init__(self):
        self.items = {}

    def reset_all(self):
        """Remove all data from this database"""
        self.items = {}

    def _get_collection_data(self, item):
        collection_name = (
            item.__name__
            if inspect.isclass(item) else item.__class__.__name__)
        if collection_name not in self.items:
            self.items[collection_name] = []
        return self.items[collection_name]

    def _get_item_index(self, item, items=None):
        if items is None:
            items = self._get_collection_data(item)
        try:
            return items.index(item)
        except ValueError:
            raise ItemNotFoundError

    def get_all(self, item_cls, sieve=None, sort=None):
        """Retrieve a list of 'item_cls' items, filtered and sorted"""
        items = self._get_collection_data(item_cls)

        # apply the filter
        if sieve is not None and len(items) > 0:
            for f_name, f_val in sieve.items():
                items = [
                    it for it in items
                    if hasattr(it, f_name) and getattr(it, f_name) == f_val]

        # apply sort rules
        if sort is not None and len(items) > 0:
            keys = tuple(k for k, _ in sort)
            reverse = any(v == SORT_DESCENDING for _, v in sort)
            items = sorted(
                items,
                key=attrgetter(*keys),
                reverse=reverse
            )

        return items

    def get_one(self, item_cls, sieve=None):
        """Retrieve an 'item_cls' item using the defined filter"""
        items = self.get_all(item_cls, sieve=sieve)
        if items is not None and len(items) == 1:
            return items[0]
        raise ItemNotFoundError

    def get_by_id(self, item_cls, item_id):
        """Retrieve an item by its ID"""
        items = self._get_collection_data(item_cls)
        try:
            return next(
                i for i in items if i.id == item_id)
        except StopIteration:
            raise ItemNotFoundError

    def save(self, new_item, mock_error=False):
        """Save an item: if ID is None then item is created else only saved"""
        if mock_error:
            raise ItemSaveError
        try:
            item = self.get_by_id(new_item, new_item.id)
        except ItemNotFoundError:
            self.create(new_item)
        else:
            # update
            self.update(item.id, new_item)
        return new_item.id

    def create(self, new_item, mock_error=False):
        ''' Create a new item'''
        if mock_error:
            raise ItemSaveError
        items = self._get_collection_data(new_item)
        new_item.id = uuid_gen()
        items.append(new_item)
        return new_item.id

    def update(self, identifier, new_item, mock_error=False):
        '''Update an existing item'''
        if mock_error:
            raise ItemSaveError
        item = self.get_by_id(new_item, identifier)
        items = self._get_collection_data(new_item)
        items[items.index(item)] = new_item
        return new_item.id

    def delete(self, item, mock_error=False):
        """Delete an item"""
        if mock_error:
            raise ItemDeleteError
        self.delete_by_id(item, item.id)

    def delete_by_id(self, item_cls, item_id):
        """Delete an item by its ID"""
        item = self.get_by_id(item_cls, item_id)
        items = self._get_collection_data(item_cls)
        index = self._get_item_index(item, items)
        del items[index]
