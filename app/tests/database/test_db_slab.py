"""Tests the interface Slab/DB"""

import pytest

from bemserver.database import SlabDB, SiteDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Slab, SurfaceInfo

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestSlabDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle slabs in the ontology."""

    def test_db_slab_get_empty(self):

        slab_db = SlabDB()

        # get all items
        result = slab_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            slab_db.get_by_id('not_existing')

    def test_db_slab_create(self, init_floors):

        floor_ids, building_ids, _ = init_floors
        slab_db = SlabDB()

        # check that database is empty
        result = slab_db.get_all()
        assert list(result) == []

        # create an item
        slab = Slab('Slab #0', floor_ids[:1], SurfaceInfo(32.3, 23, 0.9),
                    building_ids[1], kind='Roof')
        new_slab_id = slab_db.create(slab)
        assert new_slab_id is not None
        assert new_slab_id == slab.id

        # check that database is not empty now
        result = slab_db.get_all()
        slabs = list(result)
        assert len(slabs) == 1
        assert slabs[0].id == slab.id
        assert slabs[0].name == slab.name
        assert slabs[0].description == slab.description
        assert slabs[0].surface_info.area == slab.surface_info.area
        assert slabs[0].surface_info.max_height ==\
            slab.surface_info.max_height
        assert set(slabs[0].floors) == set(slab.floors)
        assert slabs[0].kind == slab.kind
        assert slabs[0].building_id == slab.building_id == building_ids[1]

        # ensure we can access the parent site
        sites = SiteDB().get_all()
        assert slab_db.get_parent(slab.id) in\
            [str(site.id) for site in sites]

    def test_db_slab_get_filter(self, init_floors):
        floor_ids, building_ids, _ = init_floors
        building_id = building_ids[0]
        slab_db = SlabDB()

        # check that database is empty
        result = slab_db.get_all(building_id=building_id)
        assert list(result) == []
        result = slab_db.get_all(space_id=floor_ids[0])
        assert list(result) == []

        # create an item
        slab_db.create(
            Slab('Slab #0', [floor_ids[0]], SurfaceInfo(32.3, 23, 0.9),
                 building_id, kind='Roof'))
        slab_db.create(
            Slab('Slab #1', floor_ids, SurfaceInfo(32.3, 23, 0.9),
                 building_id, kind='FloorSlab'))
        result = slab_db.get_all(building_id=building_id)
        assert len(list(result)) == 2

        result = slab_db.get_all(floor_id=floor_ids[0])
        assert len(list(result)) == 2
        result = slab_db.get_all(floor_id=floor_ids[1])
        assert len(list(result)) == 1

    def test_db_slab_update(self, init_slabs):

        slab_ids, _, building_ids, _ = init_slabs
        slab_db = SlabDB()
        building_id = building_ids[0]

        # get all items
        result = slab_db.get_all()
        slabs = list(result)
        assert len(slabs) == 2
        for cur_slab in slabs:
            assert cur_slab.id in slab_ids

        # get an item by its ID
        slab = slab_db.get_by_id(slabs[0].id)

        # update item data
        new_description = 'updated by patator'
        new_width = 1.65
        new_kind = 'BaseSlab'
        slab.description = new_description
        slab.surface_info.width = new_width
        slab.kind = new_kind
        slab_db.update(slab.id, slab)

        # check that item has really been updated in database
        updated_slab = slab_db.get_by_id(slab.id)
        assert updated_slab.id == slab.id
        assert updated_slab.name == slab.name
        assert updated_slab.description == new_description
        assert updated_slab.surface_info.area == slab.surface_info.area
        assert updated_slab.surface_info.max_height ==\
            slab.surface_info.max_height
        assert updated_slab.surface_info.width == new_width
        assert updated_slab.kind == new_kind
        assert set(updated_slab.floors) == set(slab.floors)
        assert updated_slab.building_id == slab.building_id == building_id

        # delete an item by its ID
        slab_db.remove(slab.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            slab_db.get_by_id(slab.id)
