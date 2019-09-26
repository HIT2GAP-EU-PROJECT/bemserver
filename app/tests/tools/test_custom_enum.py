"""Tests for hyerarchical enum extension"""

from collections import OrderedDict

from bemserver.tools.custom_enum import HierarchyEnum

from tests import TestCoreTools


class TestToolsHierarchyEnum(TestCoreTools):
    """Hierarchy enum extension tests"""

    def setup(self):
        """Set up test enum"""

        class SampleHierarchyEnum(HierarchyEnum):
            """An example of HierarchyEnum implementation"""

            family = ('Family',)
            family_son = ('Son', 'family')
            family_daughter = ('Daughter', 'family')
            family_cat = ('Cat', 'family')

            vehicle = ('Vehicle',)
            vehicle_car = ('Car', 'vehicle')
            vehicle_car_delorean = ('Time travelling car', 'vehicle_car')
            vehicle_boat = ('Boat', 'vehicle')
            vehicle_boat_lifeboat = ('Lifeboat', 'vehicle_boat')
            vehicle_boat_ship = ('Ship', 'vehicle_boat')
            vehicle_spaceship = ('Spaceship', 'vehicle')
            vehicle_spaceship_rocket = ('Space rocket', 'vehicle_spaceship')
            vehicle_spaceship_ufo = ('UFO', 'vehicle_spaceship')

            # items name does not need to contain parents name
            lvl_1 = ('Level #1',)
            lvl_2 = ('Level #2', 'lvl_1')
            lvl_3 = ('Level #3', 'lvl_2')

        self.SampleHierarchyEnum = SampleHierarchyEnum

    def test_tools_hierarchy_enum_ancestors(self):
        """Test ancestor features (parent, grand_parent, ...)"""

        # pick a 'root' (level 0) item from hierarchy
        item = self.SampleHierarchyEnum.family
        # 'root' item has no parent...
        assert not item.has_parent
        assert item.parent is None
        # ...nor grand parent
        assert item.grand_parent is None
        # 'root' item is first level of hierarchy
        assert item.level == 0
        assert item.get_ancestor_level(0) is item
        # ancestor #0 is itself
        assert item.get_ancestor(0) is item
        # no further ancestor exists
        assert item.get_ancestor(1) is None  # parent
        assert item.get_ancestor(42) is None

        # pick a level 1 item from hierarchy
        item = self.SampleHierarchyEnum.family_cat
        # item has a parent...
        assert item.has_parent
        # ...which is 'family' item
        assert item.parent is self.SampleHierarchyEnum.family
        assert item.parent_name == item.parent.name
        assert item.parent is not self.SampleHierarchyEnum.vehicle
        # no grand parent
        assert item.grand_parent is None
        # as expected item level is 1
        assert item.level == 1
        assert item.get_ancestor_level(1) is item
        # ancestor #0 is itself
        assert item.get_ancestor(0) is item
        # ancestor #1 is its parent
        assert item.get_ancestor(1) is item.parent
        # no further ancestor exists
        assert item.get_ancestor(2) is None  # grand parent
        assert item.get_ancestor(42) is None

        # pick a level 2 item from hierarchy
        item = self.SampleHierarchyEnum.vehicle_spaceship_ufo
        # item has a parent...
        assert item.has_parent
        # ...which is 'vehicle_spaceship' item (level 1)
        assert item.parent is self.SampleHierarchyEnum.vehicle_spaceship
        assert item.parent_name == item.parent.name
        assert item.grand_parent is self.SampleHierarchyEnum.vehicle
        # as expected item level is 2
        assert item.level == 2
        assert item.get_ancestor_level(2) is item
        # ancestor #0 is itself
        assert item.get_ancestor(0) is item
        # ancestor #1 is its parent
        assert item.get_ancestor(1) is item.parent
        # ancestor #2 is its grand parent
        assert item.get_ancestor(2) is item.grand_parent
        # no further ancestor exists
        assert item.get_ancestor(3) is None  # grand grand parent
        assert item.get_ancestor(42) is None
        # ancestor level 1 is item parent
        assert item.get_ancestor_level(1) is item.parent
        # ancestor level 0 is item grand parent
        assert item.get_ancestor_level(0) is item.grand_parent

    def test_tools_hierarchy_enum_sons(self):
        """Test sons features (sons, grand_sons, ...)"""

        # pick a 'root' (level 0) item from hierarchy
        item = self.SampleHierarchyEnum.family
        # item has sons
        assert item.has_sons
        # get item direct sons
        item_direct_sons = item.get_sons()
        assert len(item_direct_sons) == 3
        assert item_direct_sons == [
            self.SampleHierarchyEnum.family_son,
            self.SampleHierarchyEnum.family_daughter,
            self.SampleHierarchyEnum.family_cat]
        # get item indirect sons
        item_indirect_sons = item.get_sons(indirect=True)
        # same sons
        assert len(item_indirect_sons) == 3
        assert item_indirect_sons == item_direct_sons

        # pick a level 1 item from hierarchy
        item = self.SampleHierarchyEnum.family_cat
        # item do not have sons
        assert not item.has_sons
        # get item sons
        item_sons = item.get_sons()
        # no children, no cry...
        assert len(item_sons) == 0
        assert item_sons == []

        # pick a level 2 item from hierarchy
        item = self.SampleHierarchyEnum.vehicle_spaceship_ufo
        # item do not have sons
        assert not item.has_sons

        # with an item level 0, that have children level 1 and 2
        item = self.SampleHierarchyEnum.vehicle
        # get item direct sons
        item_sons = item.get_sons()
        assert len(item_sons) == 3
        assert item_sons == [
            self.SampleHierarchyEnum.vehicle_car,
            self.SampleHierarchyEnum.vehicle_boat,
            self.SampleHierarchyEnum.vehicle_spaceship]
        # get indirect sons (that contains all grandchildren too, it is huge!)
        item_sons = item.get_sons(indirect=True)
        assert len(item_sons) == 8
        assert item_sons == [
            self.SampleHierarchyEnum.vehicle_car,
            self.SampleHierarchyEnum.vehicle_car_delorean,
            self.SampleHierarchyEnum.vehicle_boat,
            self.SampleHierarchyEnum.vehicle_boat_lifeboat,
            self.SampleHierarchyEnum.vehicle_boat_ship,
            self.SampleHierarchyEnum.vehicle_spaceship,
            self.SampleHierarchyEnum.vehicle_spaceship_rocket,
            self.SampleHierarchyEnum.vehicle_spaceship_ufo]

    def test_tools_hierarchy_enum_label(self):
        """Test label property and breadcrumb features"""

        # pick a 'root' (level 0) item from hierarchy
        item = self.SampleHierarchyEnum.family
        # expected item label is 'Family'
        assert item.label == 'Family'
        assert item.label_breadcrumb == 'Family'
        assert item.get_label_breadcrumb() == 'Family'

        # pick a level 1 item from hierarchy
        item = self.SampleHierarchyEnum.family_cat
        # expected item label is 'Cat'
        assert item.label == 'Cat'
        # expected item label breadcrumb is 'Family - Cat'
        assert item.label_breadcrumb == 'Family - Cat'
        # or 'Family/Cat'
        assert item.get_label_breadcrumb('/') == 'Family/Cat'

        # pick a level 2 item from hierarchy
        item = self.SampleHierarchyEnum.vehicle_spaceship_ufo
        # expected item label is 'UFO'
        assert item.label == 'UFO'
        # expected item label breadcrumb is 'Vehicle - Spaceship - UFO'
        assert item.label_breadcrumb == 'Vehicle - Spaceship - UFO'
        # or 'Vehicle.Spaceship.UFO'
        assert item.get_label_breadcrumb('.') == 'Vehicle.Spaceship.UFO'

    def test_tools_hierarchy_enum_build_tree(self):
        assert self.SampleHierarchyEnum.build_hierarchy_tree() == OrderedDict([
            ('family', OrderedDict([
                ('label', 'Family'),
                ('subitems', OrderedDict([
                    ('family_son', OrderedDict([('label', 'Son')])),
                    ('family_daughter', OrderedDict([('label', 'Daughter')])),
                    ('family_cat', OrderedDict([('label', 'Cat')]))]))])),
            ('vehicle', OrderedDict([
                ('label', 'Vehicle'),
                ('subitems', OrderedDict([
                    ('vehicle_car', OrderedDict([
                        ('label', 'Car'),
                        ('subitems', OrderedDict([
                            ('vehicle_car_delorean', OrderedDict([
                                ('label', 'Time travelling car')]))]))])),
                    ('vehicle_boat', OrderedDict([
                        ('label', 'Boat'),
                        ('subitems', OrderedDict([
                            ('vehicle_boat_lifeboat', OrderedDict([
                                ('label', 'Lifeboat')])),
                            ('vehicle_boat_ship', OrderedDict([
                                ('label', 'Ship')]))]))])),
                    ('vehicle_spaceship', OrderedDict([
                        ('label', 'Spaceship'),
                        ('subitems', OrderedDict([
                            ('vehicle_spaceship_rocket', OrderedDict([
                                ('label', 'Space rocket')])),
                            ('vehicle_spaceship_ufo', OrderedDict([
                                ('label', 'UFO')]))]))]))]))])),
            ('lvl_1', OrderedDict([
                ('label', 'Level #1'),
                ('subitems', OrderedDict([
                    ('lvl_2', OrderedDict([
                        ('label', 'Level #2'),
                        ('subitems', OrderedDict([
                            ('lvl_3', OrderedDict([
                                ('label', 'Level #3')]))]))]))]))]))])

    def test_tools_hierarchy_enum_build_tree_human(self):
        assert self.SampleHierarchyEnum.build_hierarchy_tree_human() == (
            'family: Family\n'
            '  family_son: Son\n'
            '  family_daughter: Daughter\n'
            '  family_cat: Cat\n'
            'vehicle: Vehicle\n'
            '  vehicle_car: Car\n'
            '    vehicle_car_delorean: Time travelling car\n'
            '  vehicle_boat: Boat\n'
            '    vehicle_boat_lifeboat: Lifeboat\n'
            '    vehicle_boat_ship: Ship\n'
            '  vehicle_spaceship: Spaceship\n'
            '    vehicle_spaceship_rocket: Space rocket\n'
            '    vehicle_spaceship_ufo: UFO\n'
            'lvl_1: Level #1\n'
            '  lvl_2: Level #2\n'
            '    lvl_3: Level #3\n')
