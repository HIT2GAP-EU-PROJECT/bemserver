"""Tests the interface Space/DB"""

import pytest

from bemserver.database import SpaceDB, SiteDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Space, SpaceOccupancy

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestSpaceDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle spaces in the ontology."""

    def test_db_space_get_empty(self):

        space_db = SpaceDB()

        # get all items
        result = space_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            space_db.get_by_id('not_existing')

    def test_db_space_create(self, init_floors):

        floor_ids, _, _ = init_floors
        space_db = SpaceDB()

        # check that database is empty
        result = space_db.get_all()
        assert list(result) == []

        # create an item
        space_occ = SpaceOccupancy(9, 20)
        space = Space('Space #0', floor_ids[0], 'OpenSpace', space_occ)
        new_space_id = space_db.create(space)
        assert new_space_id is not None
        assert new_space_id == space.id

        # check that database is not empty now
        result = space_db.get_all()
        spaces = list(result)
        assert len(spaces) == 1
        assert spaces[0].id == space.id
        assert spaces[0].name == space.name
        assert spaces[0].description == space.description
        assert spaces[0].kind == space.kind
        assert spaces[0].occupancy.nb_max == space_occ.nb_max
        assert spaces[0].occupancy.nb_permanents == space_occ.nb_permanents
        assert spaces[0].floor_id == space.floor_id == floor_ids[0]

        # ensure we can access the parent site
        sites = SiteDB().get_all()
        assert space_db.get_parent(space.id) in [
            str(site.id) for site in sites]

    def test_db_space_update(self, init_spaces):

        space_ids, _, _, _ = init_spaces
        space_db = SpaceDB()

        # get all items
        result = space_db.get_all()
        spaces = list(result)
        assert len(spaces) == 2
        for cur_space in spaces:
            assert cur_space.id in space_ids

        # get an item by its ID
        space = space_db.get_by_id(spaces[0].id)

        # update item data
        new_description = 'updated by patator'
        new_occ_max = 12
        space.description = new_description
        space.occupancy.nb_max = new_occ_max
        space_db.update(space.id, space)

        # check that item has really been updated in database
        updated_space = space_db.get_by_id(space.id)
        assert updated_space.id == space.id
        assert updated_space.name == space.name
        assert updated_space.description == new_description
        assert updated_space.occupancy.nb_max == new_occ_max
        assert updated_space.kind == space.kind
        assert updated_space.floor_id == space.floor_id

        # delete an item by its ID
        space_db.remove(space.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            space_db.get_by_id(space.id)
