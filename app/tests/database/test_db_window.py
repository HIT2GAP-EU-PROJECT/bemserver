"""Tests the interface Window/DB"""

import pytest
from marshmallow import ValidationError

from bemserver.database import WindowDB, SiteDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Window, SurfaceInfo

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestWindowDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle windows in the ontology."""

    def test_db_window_get_empty(self):

        window_db = WindowDB()

        # get all items
        result = window_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            window_db.get_by_id('not_existing')

    def test_db_window_create(self, init_facades):

        facade_ids, _, _, _, _ = init_facades
        window_db = WindowDB()

        # check that database is empty
        result = window_db.get_all()
        assert list(result) == []

        # create an item
        window = Window('Window #0', facade_ids[0],
                        SurfaceInfo(3.3, 1.3, 0.09), covering='Curtain',
                        glazing='DoubleGlazing', u_value=54.32)
        new_window_id = window_db.create(window)
        assert new_window_id is not None
        assert new_window_id == window.id

        # check that database is not empty now
        result = window_db.get_all()
        windows = list(result)
        assert len(windows) == 1
        assert windows[0].id == window.id
        assert windows[0].name == window.name
        assert windows[0].description == window.description
        assert windows[0].surface_info.area == window.surface_info.area
        assert windows[0].surface_info.max_height ==\
            window.surface_info.max_height
        assert windows[0].surface_info.width == window.surface_info.width
        assert windows[0].covering == window.covering
        assert windows[0].glazing.replace(" ", "") == window.glazing
        assert windows[0].facade_id == window.facade_id == facade_ids[0]
        assert windows[0].u_value == window.u_value

        # ensure we can access the parent site
        sites = SiteDB().get_all()
        assert window_db.get_parent(window.id) in\
            [str(site.id) for site in sites]

        # test with wrong value for covering
        window = Window('Window #0', facade_ids[0],
                        SurfaceInfo(3.3, 1.3, 0.09), covering='Cobain',
                        glazing='DoubleGlazing', u_value=76.32)
        with pytest.raises(ValidationError):
            new_window_id = window_db.create(window)

        # test with wrong value for glazing
        window = Window('Window #0', facade_ids[0],
                        SurfaceInfo(3.3, 1.3, 0.09), covering='Curtain',
                        glazing='GFGRT')
        with pytest.raises(ValidationError):
            new_window_id = window_db.create(window)

    def test_db_window_update(self, init_windows):

        window_ids, _, _, _, _, _ = init_windows
        window_db = WindowDB()

        # get all items
        result = window_db.get_all()
        windows = list(result)
        assert len(windows) == 2
        for cur_window in windows:
            assert cur_window.id in window_ids

        # get an item by its ID
        window = window_db.get_by_id(windows[0].id)

        # update item data
        new_description = 'updated by patator'
        new_width = 1.65
        new_covering = 'Shade'
        window.description = new_description
        window.surface_info.width = new_width
        window.covering = new_covering
        window_db.update(window.id, window)

        # check that item has really been updated in database
        updated_window = window_db.get_by_id(window.id)
        assert updated_window.id == window.id
        assert updated_window.name == window.name
        assert updated_window.description == new_description
        assert updated_window.surface_info.area == window.surface_info.area
        assert updated_window.surface_info.max_height ==\
            window.surface_info.max_height
        assert updated_window.surface_info.width == new_width
        assert updated_window.covering == new_covering
        assert updated_window.glazing == window.glazing
        assert updated_window.u_value == window.u_value
        assert updated_window.facade_id == window.facade_id

        # delete an item by its ID
        window_db.remove(window.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            window_db.get_by_id(window.id)
