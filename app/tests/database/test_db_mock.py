"""Tests for database mocking"""

import pytest

from bemserver.database.exceptions import (
    ItemNotFoundError, ItemSaveError, ItemDeleteError)

from tests import TestCoreDatabaseMock
from tests.utils import uuid_gen


class TestDatabaseMock(TestCoreDatabaseMock):
    """Tests on database mock"""

    def setup(self):
        super().setup()

        class DbItem():
            """An item that can be manipulated within a database"""
            def __init__(self, name, area, description=None):
                self.id = None
                self.name = name
                self.area = area
                self.description = description

        class NotDbItem():
            """An item that can not be used in a database"""

        self.db_item_class = DbItem
        self.not_db_item_class = NotDbItem

        self.db_items = {}
        item = DbItem(name='Titty twister', area=666)
        self.db_items[self.db.save(item)] = item
        item = DbItem(name='ABC', area=999)
        self.db_items[self.db.save(item)] = item
        item = DbItem(name='ABC', area=666)
        self.db_items[self.db.save(item)] = item
        item = DbItem(name='ZYX', area=787)
        self.db_items[self.db.save(item)] = item

    def test_database_mock_get_list(self):
        """Test get_list function"""

        assert len(self.db.get_all(self.db_item_class)) == 4
        assert len(self.db.get_all(self.not_db_item_class)) == 0

        # with filtering on name
        # one occurence
        item_list = self.db.get_all(
            self.db_item_class, sieve={'name': 'Titty twister'})
        assert len(item_list) == 1
        # multiple occurences
        item_list = self.db.get_all(
            self.db_item_class, sieve={'name': 'ABC'})
        assert len(item_list) == 2
        # no occurences
        item_list = self.db.get_all(
            self.db_item_class, sieve={'name': 'not_found'})
        assert len(item_list) == 0

        # with sorting, ascending name
        item_list = self.db.get_all(self.db_item_class, sort=[('name', '1')])
        assert len(item_list) == 4
        assert item_list[0].name == 'ABC'
        assert item_list[1].name == 'ABC'
        assert item_list[2].name == 'Titty twister'
        assert item_list[3].name == 'ZYX'

        # with sorting, descending area
        item_list = self.db.get_all(self.db_item_class, sort=[('area', '-1')])
        assert len(item_list) == 4
        assert item_list[0].area == 666
        assert item_list[1].area == 666
        assert item_list[2].area == 787
        assert item_list[3].area == 999

        # with sorting, ascending area and desceding name
        item_list = self.db.get_all(
            self.db_item_class, sort=[('area', '1'), ('name', '-1')])
        assert len(item_list) == 4
        assert item_list[0].name == 'ABC'
        assert item_list[0].area == 666
        assert item_list[1].name == 'Titty twister'
        assert item_list[1].area == 666
        assert item_list[2].name == 'ZYX'
        assert item_list[2].area == 787
        assert item_list[3].name == 'ABC'
        assert item_list[3].area == 999

        # with filtering AND sorting
        item_list = self.db.get_all(
            self.db_item_class, sieve={'name': 'ABC'}, sort=[('area', '-1')])
        assert len(item_list) == 2
        assert item_list[0].area == 666
        assert item_list[1].area == 999

    def test_database_mock_get_one(self):
        """Test get_one function"""

        # find one item
        assert len(self.db_items) > 0
        item = next(iter(self.db_items.values()))

        item_found = self.db.get_one(
            self.db_item_class, sieve={'id': item.id})
        assert item_found == item
        assert item_found.id == item.id
        assert item_found.name == item.name

        # not found error
        # id do not exist
        with pytest.raises(ItemNotFoundError):
            self.db.get_one(self.db_item_class, sieve={'id': uuid_gen()})
        # multiple area result
        with pytest.raises(ItemNotFoundError):
            self.db.get_one(self.db_item_class, sieve={'area': 666})

    def test_database_mock_create(self):
        """Test save (create) function"""

        # create and save an item
        item = self.db_item_class(name='Casa bonita', area=123456)
        assert item.id is None
        item_id_before_saving = item.id
        self.db.save(item)
        assert item_id_before_saving != item.id

        # save error
        with pytest.raises(ItemSaveError):
            self.db.save(item, mock_error=True)

    def test_database_mock_find(self):
        """Test get_by_id function"""

        # find building
        assert len(self.db_items) > 0
        item = next(iter(self.db_items.values()))
        item_found = self.db.get_by_id(self.db_item_class, item.id)
        assert item_found == item
        assert item_found.id == item.id
        assert item_found.name == item.name

        # not found error
        with pytest.raises(ItemNotFoundError):
            self.db.get_by_id(self.db_item_class, str(uuid_gen()))

    def test_database_mock_update(self):
        """Test save (update) function"""

        # update and save an item
        assert len(self.db_items) > 0
        item = next(iter(self.db_items.values()))
        assert item.description is None
        item.description = 'A new description !'
        item_id_before_saving = item.id
        self.db.save(item)
        assert item_id_before_saving == item.id
        assert item.description == 'A new description !'

    def test_database_mock_delete(self):
        """Test delete function"""

        # delete an item
        assert len(self.db_items) > 0
        item = next(iter(self.db_items.values()))
        item_count_before_delete = len(self.db.get_all(self.db_item_class))
        self.db.delete(item)
        item_count_after_delete = len(self.db.get_all(self.db_item_class))
        assert item_count_after_delete < item_count_before_delete

        # item deleted is not found
        with pytest.raises(ItemNotFoundError):
            self.db.get_by_id(self.db_item_class, item.id)

        # delete error
        with pytest.raises(ItemDeleteError):
            self.db.delete(item, mock_error=True)
