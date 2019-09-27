"""Tests the interface Wall/DB"""

import pytest
from marshmallow import ValidationError

from bemserver.database import FacadeDB, SiteDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Facade, SurfaceInfo

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestWallDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle facades in the ontology."""

    def test_db_wall_get_empty(self):

        facade_db = FacadeDB()

        # get all items
        result = facade_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            facade_db.get_by_id('not_existing')

    def test_db_wall_create(self, init_spaces):

        space_ids, _, building_ids, _ = init_spaces
        facade_db = FacadeDB()

        # check that database is empty
        result = facade_db.get_all()
        assert list(result) == []

        # create an item
        facade = Facade('Facade #0', space_ids[:1], SurfaceInfo(32.3, 23, 0.9),
                        building_ids[1], 0.323, orientation='South',
                        interior=True)
        new_facade_id = facade_db.create(facade)
        assert new_facade_id is not None
        assert new_facade_id == facade.id

        # check that database is not empty now
        result = facade_db.get_all()
        facades = list(result)
        assert len(facades) == 1
        assert facades[0].id == facade.id
        assert facades[0].name == facade.name
        assert facades[0].description == facade.description
        assert facades[0].surface_info.area == facade.surface_info.area
        assert facades[0].surface_info.max_height ==\
            facade.surface_info.max_height
        assert facades[0].surface_info.width == facade.surface_info.width
        assert facades[0].windows_wall_ratio == facade.windows_wall_ratio
        assert facades[0].orientation == facade.orientation
        assert facades[0].interior == facade.interior
        assert facades[0].building_id == facade.building_id == building_ids[1]

        # ensure we can access the parent site
        sites = SiteDB().get_all()
        assert facade_db.get_parent(facade.id) in\
            [str(site.id) for site in sites]

    def test_db_facade_get_filter(self, init_spaces):
        space_ids, _, building_ids, _ = init_spaces
        building_id = building_ids[0]
        facade_db = FacadeDB()

        # check that database is empty
        result = facade_db.get_all(building_id=building_id)
        assert list(result) == []
        result = facade_db.get_all(space_id=space_ids[0])
        assert list(result) == []

        # create an item
        facade_db.create(
            Facade('Facade #0', [space_ids[0]], SurfaceInfo(32.3, 23, 0.9),
                   building_id, 0.323, interior=True))
        facade_db.create(
            Facade('Facade #1', space_ids, SurfaceInfo(32.3, 23, 0.9),
                   building_id, 0.323, interior=True))
        result = facade_db.get_all(building_id=building_id)
        assert len(list(result)) == 2

        result = facade_db.get_all(space_id=space_ids[0])
        assert len(list(result)) == 2
        result = facade_db.get_all(space_id=space_ids[1])
        assert len(list(result)) == 1

    def test_db_facade_update(self, init_facades):

        facade_ids, _, _, building_ids, _ = init_facades
        facade_db = FacadeDB()
        building_id = building_ids[0]

        # get all items
        result = facade_db.get_all()
        facades = list(result)
        assert len(facades) == 2
        for cur_facade in facades:
            assert cur_facade.id in facade_ids
            assert cur_facade.building_id == building_id

        # get an item by its ID
        facade = facade_db.get_by_id(facades[0].id)

        # update item data
        new_description = 'updated by patator'
        new_width = 1.65
        new_wwratio = 0.111111
        facade.description = new_description
        facade.surface_info.width = new_width
        facade.windows_wall_ratio = new_wwratio
        facade_db.update(facade.id, facade)

        # check that item has really been updated in database
        updated_facade = facade_db.get_by_id(facade.id)
        assert updated_facade.id == facade.id
        assert updated_facade.name == facade.name
        assert updated_facade.description == new_description
        assert updated_facade.surface_info.area == facade.surface_info.area
        assert updated_facade.surface_info.max_height ==\
            facade.surface_info.max_height
        assert updated_facade.surface_info.width == new_width
        assert updated_facade.windows_wall_ratio == new_wwratio
        assert updated_facade.interior == facade.interior
        assert updated_facade.building_id == facade.building_id == building_id

        # check something is wrong for wrong orientation
        facade.orientation = 'Wrong'
        with pytest.raises(ValidationError):
            facade_db.update(facade.id, facade)

        # delete an item by its ID
        facade_db.remove(facade.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            facade_db.get_by_id(facade.id)
