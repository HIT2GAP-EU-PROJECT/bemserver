"""Tool to manage hierarchical items in an enum"""

from collections import OrderedDict
from enum import Enum, unique as enum_unique


@enum_unique
class AutoEnum(Enum):
    """An enum class to avoid specifying numbers when creating elements"""

    def __new__(cls, *args, **kwargs):
        """Method for the creation of a new elements"""
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


@enum_unique
class HierarchyEnum(Enum):
    """An enum extension to make hierarchy.

    An item can have a parent or not.
    Infinite parent levels can be declared.

    :Example:
        2 levels hierarchy:
            # tropical climates (level 0)
            tropical = ('Tropical')
            # tropical sub climates (level 1)
            # parent is 'tropical' item
            tropical_rainforest = ('Rainforest', 'tropical')
            tropical_monsoon = ('Monsoon', 'tropical')
            tropical_savana = ('Savana', 'tropical')

        3 levels hierarchy:
            # arid climates (level 0)
            arid = ('Arid')
            # arid sub climates (level 1)
            arid_desert = ('Desert', 'arid')
            arid_steppe = ('Steppe', 'arid')
            # arid sub sub climates (level 2)
            arid_desert_hot = ('Hot', 'arid_desert')
            arid_desert_cold = ('Cold', 'arid_desert')
            arid_steppe_hot = ('Hot', 'arid_steppe')
            arid_steppe_cold = ('Cold', 'arid_steppe')
    """

    def __init__(self, label, parent_name=None):
        self._label = label
        self._parent_name = parent_name

    @property
    def label(self):
        """Return item default label."""
        return self._label

    @property
    def parent_name(self):
        """Return item parent name"""
        return self._parent_name

    @property
    def has_parent(self):
        """Return True if item has a parent"""
        return self._parent_name is not None

    @property
    def parent(self):
        """Return parent item"""
        if self.has_parent:
            return self.__class__[self._parent_name]
        return None

    @property
    def grand_parent(self):
        """Return grand parent item"""
        if self.level == 2:
            return self.parent.parent
        return None

    @property
    def has_sons(self):
        """Return True if item has at least one son"""
        for cur_item in list(self.__class__):
            if cur_item.parent is self:
                return True
        return False

    @property
    def level(self):
        """Return the item level (grand_parent=0, parent=1, child=2, ...).
        Top level is always 0 and last level is total item count less 1.
        """
        result_lvl = 0
        cur_item = self
        while cur_item.has_parent:
            cur_item = cur_item.parent
            result_lvl += 1
        return result_lvl

    @property
    def label_breadcrumb(self):
        """Return item full label, breadcrumb styled."""
        return self.get_label_breadcrumb()

    def get_label_breadcrumb(self, separator=' - '):
        """Return item label, breadcrumb styled (result is an aggregation
        of parent labels).

        :param separator: sperator string used between each item label
        """
        labels = (self.label,)
        cur_item = self
        while cur_item.has_parent:
            cur_item = cur_item.parent
            labels = (cur_item.label,) + labels
        return (separator or ' - ').join(labels)

    def get_ancestor(self, nb_level_back=0):
        """Return an ancestor item from item, at the specified number of
        level backwards. If ancestor item not exist, None is returned.

        :param nb_level_back: number of levels to reach backwards
        """
        cur_item = self
        nb_level_done = 0
        while cur_item.has_parent and nb_level_done != nb_level_back:
            cur_item = cur_item.parent
            nb_level_done += 1
        if nb_level_done == nb_level_back:
            return cur_item
        return None

    def get_ancestor_level(self, level=0):
        """Return an ancestor item at specified level. If level does not exist,
        None is returned.

        :param level: level of the ancestor to get
        """
        cur_item = self
        while cur_item.has_parent and cur_item.level != level:
            cur_item = cur_item.parent
        if cur_item.level == level:
            return cur_item
        return None

    def get_sons(self, indirect=False):
        """Return a list of all direct children items.
        If no sons, returns None.

        :param indirect: True to return all children and grandchildren
        """
        sons = []
        for cur_item in list(self.__class__):
            if cur_item.parent is self:
                sons.append(cur_item)
                if indirect:
                    # get grandchildren too and propagate indirect
                    sons.extend(cur_item.get_sons(indirect=indirect))
        return sons

    @classmethod
    def build_hierarchy_tree(cls):
        """Return enum hierarchy tree"""
        def build_item(item):
            subitems = [
                i for i in cls
                if (i.level == item.level + 1) and (i.parent == item)]
            item_dump = OrderedDict((('label', item.label), ))
            if subitems:
                item_dump['subitems'] = OrderedDict(
                    [(s.name, build_item(s)) for s in subitems])
            return item_dump
        return OrderedDict([
            (item.name, build_item(item)) for item in cls if item.level == 0])

    @classmethod
    def build_hierarchy_tree_human(cls, indent=2):
        """Return enum hierarchy tree in a human-friendly representation

        :param int indent: Number of indentation spaces per level
        """
        def build_item(item):
            subitems = [
                i for i in cls
                if (i.level == item.level + 1) and (i.parent == item)]
            item_dump = '{}{}: {}\n'.format(
                ' ' * indent * item.level, item.name, item.label)
            for sub in subitems:
                item_dump += build_item(sub)
            return item_dump
        return ''.join([build_item(item) for item in cls if item.level == 0])
