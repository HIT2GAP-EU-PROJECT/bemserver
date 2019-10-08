"""Serialize/deserialize quantity elements into the data storage solution.

All elements are related with concepts in the QUDT ontology
"""
# pylint: disable=no-member

import abc

from .schemas import QuantitySchema
from .utils import str_insert
from .ontology.manager import SPARQLOP, PREFIX, ontology_manager_factory
from .utils import generate_id
from .exceptions import ItemNotFoundError


class QuantityDAO(abc.ABC):
    """An interface for Data Access Object Pattern realization"""

    @abc.abstractmethod
    def get(self, url):
        """Get a quantity/quantityValue accordng to its id
        :url string: URI associated to the concepts.
        :return a Quantity object"""

    @abc.abstractmethod
    def create(self, quantity):
        """Create a quantity; it is a couple numeric value, unit
        :quantity Quantity with all the required values
        :url string the url of the Quantity to create if required"""

    @abc.abstractmethod
    def remove(self, url):
        """Remove a quantity identified by its url
        :url string: the URL of the quantity to remove"""

    @abc.abstractmethod
    def update(self, url, new_quantity):
        """Update the quantity identified by its url
        :url string: the URL of the quantity to update
        :new_quantity Quantity: the new Quantity"""

    @abc.abstractmethod
    def get_all_uris_for(self, url, relation=None, kind=None):
        """Get all quantity/quantityValue accordng associated to the url. If
        required, the search is restricted to the relation given in parameter
        :url string: URI associated to the concepts.
        :relation string: the name of the relation used as a filter
        :kind string: the quantity kind
        :return a list of URIs"""


class QuantityDB(QuantityDAO):
    """Quantity interface with the QUDT ontology"""

    QUANTITY = {
        'value': PREFIX.PROPERTY.alias_uri('propertyValue'),
        'unit': PREFIX.PROPERTY.alias_uri('hasUnit'),
    }

    SELECT = """SELECT ?kind ?unit ?value
                WHERE {{{{
                    ?kind rdfs:subClassOf* {0}.
                    {{uri}} a ?kind;
                           {1} ?value;
                           {2} ?unit.
            }}}}""".format(PREFIX.PROPERTY.alias_uri('PhenomenonProperty'),
                           QUANTITY["value"],
                           QUANTITY["unit"])

    def __init__(self):
        self.onto_mgr = ontology_manager_factory.get_ontology_manager()

    def _to_object(self, binding):
        """Make Quantity instance from SPARQL query binding

        :param dict binding: Element of QueryResult.result
        """
        binding['unit'] = PREFIX.get_name(binding['unit'])
        binding['kind'] = PREFIX.get_name(binding['kind'])
        return QuantitySchema().load(binding).data

    def _build_select_query(self, uri):
        """A method to build the select query
        :return string: a string for the SPARQL query"""
        return self.SELECT.format(uri=uri)

    def get(self, url):
        query = self._build_select_query(url)
        result = self.onto_mgr.perform(SPARQLOP.SELECT, query)
        try:
            bind = result.values[0]
        except IndexError:
            raise ItemNotFoundError
        return self._to_object(bind)

    def create(self, quantity):
        """Create a quantity

        :param quantity: a quantity object
        :return: a JSON that validates the creation of these quantities
        """
        _id = str(generate_id())
        _url = PREFIX.PROPERTY.alias_uri(_id)
        # Build the query
        query = """INSERT DATA {{
                {0} a {1};
                """.format(_url,
                           PREFIX.PROPERTY.alias_uri(quantity.kind))
        query += str_insert(self.QUANTITY, quantity, "value")
        query += str_insert(
            self.QUANTITY, quantity, "unit", prefix=PREFIX.UNIT, optional=True)
        query += "}"
        self.onto_mgr.perform(SPARQLOP.INSERT, query)
        return _id

    def create_for(self, quantity, relation, parent_url):  # , url=None):
        """Create a quantity associated to a concept.

        :quantity Quantity: an instance of Quantity
        :relation string: the URI for the relation to connect the quantity with
            the element
        :parent_url string: the URI of the parent element.
        :return A dictionary as JSON
        """
        _id = self.create(quantity)
        query = 'INSERT DATA {{{} {} {}}}'.format(
            parent_url, relation, PREFIX.PROPERTY.alias_uri(_id))
        self.onto_mgr.perform(SPARQLOP.INSERT, query)
        return _id

    def remove(self, url):
        """Remove a quantity identified by its id
        :identifier uuid: an identifier for the element to remove"""
        # Build query
        query = """DELETE {{?s ?p ?o}}
                   WHERE {{
                     VALUES ?s {{{0}}}.
                     ?s ?p ?o.
                }}""".format(url)
        self.onto_mgr.perform(SPARQLOP.DELETE, query,)

    def update(self, url, new_quantity):
        """Update the quantity identified by its URL, and replace it according to the
        values in parameters

        :url string: the URL for the quantity to be updated
        :new_quantity Quantity: the new quantity that should replace the one
            identified by URL
        """
        # TODO: should be a DELETE... INSERT...?
        self.remove(url)
        # return self.create(new_quantity, url)
        return self.create(new_quantity)

    def get_all_for(self, url, relation=None, kind=None):
        """Get all quantity/quantityValue accordng associated to the url. If
        required, the search is restricted to the relation given in parameter

        :url string: URI associated to the concepts.
        :relation string: the name of the relation used as a filter
        :return a list of Quantity objects
        """
        uris = self.get_all_uris_for(url, relation=relation, kind=kind)
        return (self.get(uri) for uri in uris)

    def get_all_uris_for(self, url, relation=None, kind=None):
        """Get all URIS associated to the url. If
        required, the search is restricted to the relation given in parameter

        :url string: URI associated to the concepts.
        :relation string: the name of the relation used as a filter
        :return a list of URIs
        """
        _relation = "?p" if not relation else relation
        if kind is None:
            _kind = PREFIX.PROPERTY.alias_uri('PhenomenonProperty')
        else:
            _kind = PREFIX.PROPERTY.alias_uri(kind)
        # Build query
        query = """SELECT ?uri
                   WHERE {{
                       {} {} ?uri.
                       ?class rdfs:subClassOf* {}.
                       ?uri a ?class.
                   }}""".format(url, _relation, _kind)
        result = self.onto_mgr.perform(SPARQLOP.SELECT, query)
        # Build list of URIs
        return ['<{}>'.format(binding['uri']) for binding in result.values]
