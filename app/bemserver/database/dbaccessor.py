"""Database accessor

Retrieves data from database.
"""

import inspect

from .db_mock import DatabaseMock


class DBAccessor():
    """Database accessor class"""

    def __init__(self):
        self._db = DatabaseMock()
        self.db_handlers = {}

    def set_handler(self, handlers):
        '''Initialize handlers
        :param handlers dictionary: The dictionary used to identify handlers.
            Maps classes from the models to DB handler objects'''
        self.db_handlers = handlers

    def _get_handler(self, item):
        '''Obtains the correct DB handler based on item - which is supposed to
        be an object or a class. The default handler is self._db
        :param item Object: an object or class for which there should be a DB
            handler
        :returns Object: a DB handler'''
        class_ = item if inspect.isclass(item) else item.__class__
        return (self.db_handlers[class_] if class_ in self.db_handlers else
                self._db,
                class_ not in self.db_handlers)

    def reset_db(self):
        """Remove all data from database"""
        self._db.reset_all()

    def _preprocess_save(self, item, **kwargs):
        """Save an item: if ID is None then item is created else only saved
        :param item Object: an Object or a Class to be saved"""
        # tricky case to mock a save error...
        try:
            return 'save_error' in item.name
        except AttributeError:
            return kwargs.pop('save_error', False)
        # try:
        #     item_ = self.get_by_id(item, new_item.id)
        # except ItemNotFoundError:
        # self.create(item)
        # else:
        #     # update
        #     self.update(item.id, new_item)
        # return new_item

    def create(self, item, **kwargs):
        """Create a new item"""
        mock_error = self._preprocess_save(item, **kwargs)
        db_handler, is_mock = self._get_handler(item)
        return db_handler.create(item, mock_error) if is_mock\
            else db_handler.create(item)

    def update(self, item, **kwargs):
        """Create a new item"""
        mock_error = self._preprocess_save(item, **kwargs)
        db_handler, is_mock = self._get_handler(item)
        return db_handler.update(item.id, item, mock_error) if is_mock\
            else db_handler.update(item.id, item)

    def delete(self, item, **kwargs):
        """Delete an item
        :param item Object: the element to be removed"""
        # tricky case to mock a delete error...
        try:
            mock_error = ('delete_error' in item.name)
        except AttributeError:
            mock_error = kwargs.pop('delete_error', False)
        handler, is_mock = self._get_handler(item)
        return handler.remove(item.id) if not is_mock\
            else handler.delete(item, mock_error)

    def get_item_by_id(self, item_cls, item_id):
        """Retrieve an item by its ID"""
        handler, is_mock = self._get_handler(item_cls)
        return handler.get_by_id(item_id) if not is_mock\
            else self._db.get_by_id(item_cls, item_id)

    def get_list(self, item_cls, sieve=None, sort=None):
        """Retrieve a list of items"""
        handler, is_mock = self._get_handler(item_cls)
        return list(handler.get_all(**sieve if sieve else {})) if not is_mock\
            else self._db.get_all(item_cls=item_cls, sieve=sieve, sort=sort)

    def get_parent(self, item_cls, item_id):
        """Get the parent ID if the object identified by item_id. For control
        access purpose"""
        handler, is_mock = self._get_handler(item_cls)
        return handler.get_parent(item_id) if not is_mock\
            else None
