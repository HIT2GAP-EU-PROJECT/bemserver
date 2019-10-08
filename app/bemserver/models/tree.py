"""A tree model
Used for hierarchical types"""

from .exceptions import TreeNodeAlreadyHasParentError


class Node():
    """A node in a tree. Defined by its children and parent."""

    def __init__(self, name, *, label=None):
        self.name = name
        self.label = label or name
        self._children = []
        self._parent = None

    @property
    def parent(self):
        """Return the parent of current node."""
        return self._parent

    @property
    def level(self):
        """Return the level number of item."""
        if self.has_parent:
            return self._parent.level + 1
        return 0

    @property
    def children(self):
        """Returns the list of children"""
        return self._children

    def add_child(self, child_node):
        """Adds a node to the set of children of the current node.

        :param Node child_node: A child node.
        """
        # child_node must have a unique parent
        if child_node.has_parent and child_node.parent != self:
            raise TreeNodeAlreadyHasParentError(child_node.parent.label)
        # add child_node only if it is not already a son of current node
        if child_node not in self._children:
            child_node._parent = self
            self._children.append(child_node)

    def add_children(self, children):
        """Adds a set of nodes to the set of children of current node.

        :param list[Node] children: A set of children nodes.
        """
        for child in children:
            self.add_child(child)

    @property
    def has_parent(self):
        """Return True if the node is not orphan."""
        return self.parent is not None

    @property
    def has_sons(self):
        """Return True if the node is not a terminal one."""
        return len(self._children) > 0

    def get_son(self, son_name, indirect=False):
        """Return a direct son using the specified name.
        Return `None` if not found.

        :param str son_name: The son's name to find.
        :param bool indirect: If True also search in grandchildren.
        """
        for child in self.children:
            if child.name == son_name:
                return child
            if indirect:
                gd_child = child.get_son(son_name, indirect=indirect)
                if gd_child is not None:
                    return gd_child
        return None

    def get_sons(self, indirect=False):
        """Return a list of all direct children items.

        :param bool indirect: If True also returns grandchildrens.
        """
        sons = []
        for child in self._children:
            sons.append(child)
            if indirect:
                # get grandchildrens too and propagate indirect
                sons.extend(child.get_sons(indirect=indirect))
        return sons

    def get_son_names(self, indirect=False):
        """Return a list of all direct children name.

        :param bool indirect: If True also returns grandchildrens.
        """
        son_names = []
        for child in self._children:
            son_names.append(child.name)
            if indirect:
                # get grandchildrens too and propagate indirect
                son_names.extend(child.get_son_names(indirect=indirect))
        return son_names

    def get_names(self):
        """Returns the list of names in the tree"""
        labels = [self.name]
        for child in self._children:
            labels.extend(child.get_names())
        return labels

    @property
    def label_breadcrumb(self):
        """Return item full label, breadcrumb styled."""
        return self.get_label_breadcrumb()

    def get_label_breadcrumb(self, separator=' - '):
        """Return item label, breadcrumb styled (aggregation of parent labels).

        :param str separator: Separator string used between each item label.
        """
        labels = (self.label,)
        cur_node = self
        while cur_node.has_parent:
            cur_node = cur_node.parent
            labels = (cur_node.label,) + labels
        return (separator or ' - ').join(labels)

    def __str__(self):
        def _to_str(node, indent=0):
            res = '{}{}\n'.format('\t'*indent, node.label)
            for child in node.children:
                res = res + _to_str(child, indent=indent+1)
            return res
        return _to_str(self)

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'level={self.level}'
            ', name="{self.name}"'
            ', label="{self.label}"'
            ', has_parent={self.has_parent}'
            ', has_sons={self.has_sons}'
            ')'.format(self=self))
