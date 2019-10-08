"""Tests for base data model (Thing model)"""

from abc import ABC
import datetime as dt
import pytz
import pytest

from bemserver.models.thing import Thing
from bemserver.tools.common import check_list_instances

from tests import TestCoreModel
from tests.utils import uuid_gen


class TestModelThing(TestCoreModel):
    """Thing model tests"""

    def test_model_thing_abstraction(self):
        """Test Thing model abstraction"""

        # as it is an absctract class, Thing can not be instantiated itself
        assert issubclass(Thing, ABC)
        with pytest.raises(TypeError):
            Thing()

        # inherited class does not implement abstract methods
        with pytest.raises(TypeError):
            class WrongStuff(Thing):
                pass
            WrongStuff()

        # define a class with abstract methods implemented
        class GoodStuff(Thing):
            def __init__(self):
                super().__init__()
        good_stuff = GoodStuff()
        assert good_stuff.id is None

    def test_model_thing_repr(self):
        """Test Thing model repr"""

        class Ecologist(Thing):
            def __init__(self, name):
                super().__init__()
                self.name = name

        ecolo = Ecologist(name='José')
        assert ecolo.id is None
        assert ecolo.name == "José"

    def test_model_thing_update(self):
        """Test Thing model update function"""

        class Poppy(Thing):
            def __init__(self):
                super().__init__()
                self.color = 'red'
                self.smelling = 'strong'

        a_poppy = Poppy()
        assert a_poppy.color == 'red'
        assert a_poppy.smelling == 'strong'
        a_poppy.update({'color': 'orange', 'smelling': 'light'})
        assert a_poppy.color == 'orange'
        assert a_poppy.smelling == 'light'
        a_poppy.update({'color': 'red & yellow'})
        assert a_poppy.color == 'red & yellow'
        assert a_poppy.smelling is 'light'

    def test_model_thing_update_complex(self):
        """Test Thing model update function (class contain nested `Thing`)"""

        class Table(Thing):
            def __init__(self, nb_seats):
                super().__init__()
                self.nb_seats = nb_seats

        class Restaurant(Thing):
            _tables = []

            def __init__(self, name, tables):
                super().__init__()
                self.name = name
                self.tables = tables

            @property
            def tables(self):
                return self._tables

            @tables.setter
            def tables(self, value):
                if check_list_instances(value, Table):
                    self._tables = value
                elif check_list_instances(value, dict):
                    self._tables = [Table(**cur_value) for cur_value in value]
                else:
                    raise ValueError('Invalid tables: {}'.format(value))

        with pytest.raises(ValueError):
            Restaurant(name='wrong_tables', tables='wrong')

        restaurant = Restaurant(
            name='Chez Pépé', tables=[Table(4), Table(2), Table(8)])
        assert restaurant.name == 'Chez Pépé'
        assert len(restaurant.tables) == 3

        # update tables
        restaurant.tables[0].update({'nb_seats': 6})
        assert len(restaurant.tables) == 3
        assert restaurant.tables[0].nb_seats == 6

        restaurant.update({'tables': [Table(12)]})
        assert restaurant.name == 'Chez Pépé'
        assert len(restaurant.tables) == 1
        assert restaurant.tables[0].nb_seats == 12

    def test_model_thing_dump(self):
        """Test Thing model dump function"""

        class Grain(Thing):
            def __init__(self, cereal, quantity, expiration_date=None):
                super().__init__(id=uuid_gen())
                self.cereal = cereal
                self.quantity = quantity
                self.expiration_date = expiration_date

        grain = Grain(
            cereal='rice', quantity=42,
            expiration_date=dt.datetime(2012, 12, 12))
        assert grain.dump() == {
            'id': str(grain.id), 'cereal': grain.cereal,
            'quantity': grain.quantity,
            'expiration_date': pytz.utc.localize(
                grain.expiration_date).isoformat()}
        assert grain.dump(exclude=('id',)) == {
            'cereal': grain.cereal, 'quantity': grain.quantity,
            'expiration_date': pytz.utc.localize(
                grain.expiration_date).isoformat()}

        # 'None' values are excluded
        grain = Grain(cereal='corn', quantity=69)
        assert grain.dump() == {
            'id': str(grain.id), 'cereal': grain.cereal,
            'quantity': grain.quantity}
        assert grain.dump(exclude=('id',)) == {
            'cereal': grain.cereal, 'quantity': grain.quantity}

        # include 'None' values
        grain = Grain(cereal='corn', quantity=69)
        assert grain.dump(exclude_none=False) == {
            'id': str(grain.id), 'cereal': grain.cereal,
            'quantity': grain.quantity, 'expiration_date': None}
        assert grain.dump(exclude=('id',), exclude_none=False) == {
            'cereal': grain.cereal, 'quantity': grain.quantity,
            'expiration_date': None}

    def test_model_thing_dump_complex(self):
        """Test Thing model dump function (class contain nested `Thing`)"""

        class Floor(Thing):
            def __init__(self, level, area=None):
                super().__init__()
                self.level = level
                self.area = area

        class House(Thing):
            _floors = []

            def __init__(self, address, floors):
                super().__init__()
                self.address = address
                self.floors = floors

            @property
            def floors(self):
                return self._floors

            @floors.setter
            def floors(self, value):
                if check_list_instances(value, Floor):
                    self._floors = value
                elif check_list_instances(value, dict):
                    self._floors = [Floor(**cur_value) for cur_value in value]
                else:
                    raise ValueError('Invalid floors: {}'.format(value))

        with pytest.raises(ValueError):
            House(address='far far away', floors='wrong')

        house = House(
            address='over there', floors=[Floor(-1), Floor(0), Floor(1)])
        assert house.address == 'over there'
        assert len(house.floors) == 3

        # dump
        assert house.address == 'over there'
        assert house.floors is not None and len(house.floors) > 0
        assert house.floors[0].level == -1
        assert house.floors[1].level == 0
        assert house.floors[2].level == 1
