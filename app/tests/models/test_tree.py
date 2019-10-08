"""Tests for Node object."""

import pytest

from bemserver.models.tree import Node
from bemserver.models.exceptions import TreeNodeAlreadyHasParentError

from tests import TestCoreModel


class TestModelTree(TestCoreModel):
    """Tree node model tests."""

    def setup(self):
        """Set up test tree node."""

        vehicle_tree = Node('vehicle', label='Vehicle')

        car_node = Node('car', label='Car')
        vehicle_tree.add_child(car_node)
        delorean_node = Node('delorean', label='Time travelling machine')
        car_node.add_child(delorean_node)

        boat_node = Node('boat', label='Boat')
        boat_node.add_child(Node('lifeboat', label='Lifeboat'))
        boat_node.add_child(Node('ship', label='Ship'))
        vehicle_tree.add_child(boat_node)

        spaceship_node = Node('spaceship', label='Spaceship')
        spaceship_node.add_children([
            Node('space_rocket', label='Space rocket'),
            Node('ufo', label='UFO')])
        vehicle_tree.add_child(spaceship_node)

        self.vehicle_tree = vehicle_tree
        self.car_node = car_node
        self.delorean_node = delorean_node

    def test_model_tree_node_element(self):
        """Test tree node element."""

        assert self.vehicle_tree.name == 'vehicle'
        assert self.vehicle_tree.label == 'Vehicle'
        assert self.vehicle_tree.level == 0
        assert not self.vehicle_tree.has_parent
        assert self.vehicle_tree.parent is None
        assert self.vehicle_tree.has_sons
        assert len(self.vehicle_tree.children) == 3

        assert len(self.vehicle_tree.get_sons()) == 3
        assert len(self.vehicle_tree.get_sons(indirect=True)) == 8

        assert len(self.vehicle_tree.get_son_names()) == 3
        assert len(self.vehicle_tree.get_son_names(indirect=True)) == 8

        assert self.vehicle_tree.get_son('car') == self.car_node
        assert self.vehicle_tree.get_son('delorean') is None
        assert self.vehicle_tree.get_son(
            'delorean', indirect=True) is self.delorean_node

        assert self.delorean_node.parent == self.car_node
        assert self.delorean_node in self.car_node.children
        assert self.delorean_node.level > self.car_node.level

    def test_model_tree_node_parent_level(self):
        """Test tree node parent and level stuff."""

        vehicle_tree = Node('vehicle', label='Vehicle')
        assert vehicle_tree.level == 0

        boat_node = Node('boat', label='Boat')
        assert not boat_node.has_parent
        assert boat_node.level == 0
        vehicle_tree.add_child(boat_node)
        assert boat_node.has_parent
        assert boat_node.level == 1

        lifeboat_node = Node('lifeboat', label='Lifeboat')
        assert not lifeboat_node.has_parent
        assert lifeboat_node.level == 0
        boat_node.add_child(lifeboat_node)
        assert lifeboat_node.has_parent
        assert lifeboat_node.parent == boat_node
        assert lifeboat_node.level == 2

        assert len(boat_node.children) == 1
        boat_node.add_child(lifeboat_node)
        assert len(boat_node.children) == 1

    def test_model_tree_node_label_breadcrumb(self):
        """Test tree node element, label breadcrumb."""

        # pick the 'root' (level 0) node
        root_node = self.vehicle_tree
        # expected label is 'Vehicle'
        assert root_node.label == 'Vehicle'
        assert root_node.label_breadcrumb == 'Vehicle'
        assert root_node.get_label_breadcrumb() == 'Vehicle'

        # pick a level 1 node (root's son)
        car_node = self.vehicle_tree.get_son('car')
        # expected label is 'Car'
        assert car_node.label == 'Car'
        # expected label breadcrumb is 'Vehicle - Car'
        assert car_node.label_breadcrumb == 'Vehicle - Car'
        # or 'Root/2nd child'
        assert car_node.get_label_breadcrumb('/') == 'Vehicle/Car'

        # pick a level 2 node (root's grandchildren)
        delorean_node = self.vehicle_tree.get_son('delorean', indirect=True)
        # expected label is 'Time travelling machine'
        assert delorean_node.label == 'Time travelling machine'
        # expected label breadcrumb: 'Vehicle - Car - Time travelling machine'
        assert delorean_node.label_breadcrumb == (
            'Vehicle - Car - Time travelling machine')
        # or 'Vehicle.Spaceship.UFO'
        assert delorean_node.get_label_breadcrumb(
            ' |> ') == 'Vehicle |> Car |> Time travelling machine'

    def test_model_tree_node_errors(self):
        """Tests tree node exceptions."""

        vehicle_tree = Node('vehicle', label='Vehicle')

        spaceship_node = Node('spaceship', label='Spaceship')
        vehicle_tree.add_child(spaceship_node)

        rocket_node = Node('space_rocket', label='Space rocket')
        spaceship_node.add_child(rocket_node)

        # rocket_node can not be a child of spaceship_node and vehicle_tree
        # a node has a unique parent
        with pytest.raises(TreeNodeAlreadyHasParentError):
            vehicle_tree.add_child(rocket_node)
