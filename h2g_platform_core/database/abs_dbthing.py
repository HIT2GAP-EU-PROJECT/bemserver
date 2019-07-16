"""A module for common operation on Thing"""

import abc

class DBThing(metaclass=abc.ABCMeta):
    """Abstract class for handling resources (in Models) in the Database"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def get(self, params_select):
        """Get a resource - parameters are specificed in a dictionary - returns an object"""
        pass

    @abc.abstractmethod
    def get_all(self, params_select):
        """Get a list of object based on the parameters passed in a ditionary"""
        pass

    @abc.abstractmethod
    def remove(self, thing):
        """Removes a resource in the database"""
        pass

    @abc.abstractmethod
    def add(self, things):
        """Add resources in the database"""
        pass
