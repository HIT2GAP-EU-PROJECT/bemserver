"""Exceptions of the ontology interface"""


class MissingValueError(Exception):
    """A value is expected for the creation of a new object"""


class MissingElementError(Exception):
    """Missing element error"""


class SPARQLError(Exception):
    """SPARQL operation error"""
