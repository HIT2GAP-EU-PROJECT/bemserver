"""Tests the interface Quantity/DB"""

import pytest

from bemserver.models.quantity import Quantity
from bemserver.database.db_quantity import QuantityDB
from bemserver.database.ontology.manager import PREFIX
from bemserver.database.exceptions import ItemNotFoundError


class TestDBQuantity():
    """Unit tests on the interface to handle Quantities in the ontology"""

    def _create_quantity(self):
        my_quantity = Quantity("Area", 323.324, "SquareMeter")
        return my_quantity

    def _assert_equal(self, quantity1, quantity2):
        assert quantity1.kind == quantity2.kind
        assert quantity1.unit == quantity2.unit
        assert quantity1.value == quantity2.value

    def _remove(self, url):
        quantity_db = QuantityDB()
        quantity_db.remove(url)

    @pytest.mark.usefixtures('init_onto_mgr_fact')
    def test_db_quantity(self):
        quantity = Quantity("Area", 323.324, "SquareMeter")
        quantity_db = QuantityDB()
        _id = quantity_db.create(quantity)
        uri = PREFIX.PROPERTY.alias_uri(_id)
        dummy_uri = PREFIX.PROPERTY.alias_uri('dummy')
        quantity_get = quantity_db.get(uri)
        self._assert_equal(quantity, quantity_get)
        with pytest.raises(ItemNotFoundError):
            quantity_get = quantity_db.get(dummy_uri)
        quantity_db.remove(uri)
        with pytest.raises(ItemNotFoundError):
            quantity_get = quantity_db.get(uri)

#     def test_create_get(self):
#         """Basic test: create a quantity in the model and find it back"""
#         quantity_db = QuantityDB()
#         my_quantity = self._create_quantity()
#         name = PREFIX.ROOT.alias+":surface"
#         quantity_db.create(my_quantity, name)
#         result = quantity_db.get(name)
#         self._remove(name)

    @pytest.mark.skip
    def test_create_wrong_unit(self):
        """Basic test: create a quantity in the model and find it back"""
        quantity_db = QuantityDB()
        my_quantity = self._create_quantity()
        my_quantity._unit = "Wrong"
        name = PREFIX.QUDT.alias_uri('wrongUnit')
        quantity_db.create(my_quantity, name)
        self._remove(name)

    @pytest.mark.skip
    def test_create_wrong_kind(self):
        """Basic test: create a quantity in the model and find it back"""
        quantity_db = QuantityDB()
        my_quantity = self._create_quantity()
        my_quantity._kind = "Wrong"
        name = PREFIX.QUDT.alias_uri('wrongSurface')
        quantity_db.create(my_quantity, name)
        self._remove(name)

    @pytest.mark.skip
    def test_create_clash_unit_kind(self):
        """Basic test: create a quantity in the model and find it back"""
        quantity_db = QuantityDB()
        my_quantity = self._create_quantity()
        my_quantity._unit = "Centimeter"
        name = PREFIX.QUDT.alias_uri('clash')
        quantity_db.create(my_quantity, name)
        self._remove(name)
