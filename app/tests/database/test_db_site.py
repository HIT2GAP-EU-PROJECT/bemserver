"""Tests the interface Site/DB"""

import pytest

from bemserver.database import SiteDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import Site, GeographicInfo

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestSiteDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle sites in the ontology."""

    def test_db_site_get_empty(self):

        site_db = SiteDB()

        # get all items
        result = site_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            site_db.get_by_id('not_existing')

    def test_db_site_create(self):

        site_db = SiteDB()

        # check that database is empty
        result = site_db.get_all()
        assert list(result) == []

        # create an item
        geo_info = GeographicInfo(44.803652, -0.600954, altitude=20)
        site = Site('Site #0', geo_info)
        new_site_id = site_db.create(site)
        assert new_site_id is not None
        assert new_site_id == site.id

        # check that database is not empty now
        result = site_db.get_all()
        sites = list(result)
        assert len(sites) == 1
        assert sites[0].id == site.id
        assert sites[0].name == site.name
        assert sites[0].description == site.description
        assert sites[0].geographic_info.latitude == geo_info.latitude
        assert sites[0].geographic_info.longitude == geo_info.longitude
        assert sites[0].geographic_info.altitude == geo_info.altitude

        # ensure we can access the parent site
        assert site_db.get_parent(site.id) == str(site.id)

        # test filtering parent site in the query
        sites = site_db.get_all(sites=['afakeid', site.id])
        assert {site_.id for site_ in sites} == {site.id}

    def test_db_site_get_update_delete(self, init_sites):

        site_ids = init_sites
        site_db = SiteDB()

        # get all items
        result = site_db.get_all()
        sites = list(result)
        assert len(sites) == 2
        for cur_site in sites:
            assert cur_site.id in site_ids

        # get an item by its ID
        site = site_db.get_by_id(sites[0].id)

        # update item data
        new_description = 'updated by patator'
        new_altitude = 42
        site.description = new_description
        site.geographic_info.altitude = new_altitude
        site_db.update(site.id, site)

        # check that item has really been updated in database
        updated_site = site_db.get_by_id(site.id)
        assert updated_site.id == site.id
        assert updated_site.name == site.name
        assert updated_site.description == new_description
        assert (updated_site.geographic_info.latitude ==
                site.geographic_info.latitude)
        assert (updated_site.geographic_info.longitude ==
                site.geographic_info.longitude)
        assert updated_site.geographic_info.altitude == new_altitude

        # delete an item by its ID
        site_db.remove(site.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            site_db.get_by_id(site.id)
