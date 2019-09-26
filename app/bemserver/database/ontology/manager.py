"""Module related to the usage of the Apache Jena/Fuseki RDF triple store"""

import enum
import urllib
import logging

import SPARQLWrapper as sprqlw

from .exceptions import SPARQLError
from ...tools.custom_enum import AutoEnum


logger = logging.getLogger('bemserver')


class SPARQLOP(AutoEnum):
    """Enumeration of the different type of SPARQL operations available"""
    SELECT = ()
    ASK = ()
    INSERT = ()
    UPDATE = ()
    DELETE = ()


@enum.unique
class PREFIX(enum.Enum):
    """Enumeration of the different ontologies that can be used."""

    def __init__(self, alias, url):
        self.alias = alias
        self.url = url

    def alias_uri(self, name):
        """Build aliased URI from enum alias and name"""
        return '{}:{}'.format(self.alias, name)

    @staticmethod
    def get_name(uri):
        """Strip name from (unaliased) URI"""
        for prefix in PREFIX:
            try:
                _, name = uri.split(prefix.url)
                return name
            except ValueError:
                pass
        raise ValueError('Invalid OWL URI: {}'.format(uri))

    PROPERTY = ('pty', 'http://bemserver.org/property#')
    BUILDING_INFRA = ('bi', 'http://bemserver.org/building#')
    OCCUPANT = ('occ', 'http://bemserver.org/occupant#')
    SERVICES = ('services', 'http://bemserver.org/services#')
    ROOT = ('bem', 'http://bemserver.org#')

    IFC2x3 = (
        'ifc2x3', 'http://www.buildingsmart-tech.org/ifcOWL/IFC2X3_Final#')
    IFC4 = ('ifc4', 'http://ifcowl.openbimstandards.org/IFC4_ADD2/index.html#')
    ONTO_MG = ('mg', 'http://hit2gap.eu/ontomg#')
    SSN = ('ssn', 'http://www.w3.org/ns/ssn/')
    SOSA = ('sosa', 'http://www.w3.org/ns/sosa/')
    QUDT = ('qudt', 'http://qudt.org/schema/qudt#')
    UNIT = ('unit', 'http://qudt.org/vocab/unit#')
    OWL = ('owl', 'http://www.w3.org/2002/07/owl#')
    RDFS = ('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
    RDF = ('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    HYDRA = ('hydra', 'http://www.w3.org/ns/hydra/core#')
    SCHEMA = ('schema', 'http://schema.org/')


class QueryResult:
    """A simple class to encapsulate relevant informations for results"""

    def __init__(self, values=None, message=None):
        """Value only required for SELECT operations; message
        required for all other operations.

        :param list values: list of dictionaries,
            keys are strings (i.e. variable name in the query)
            values can be numeric, date, string...
        :param str message: associated message
        """
        self.values = values or []
        self.message = message

    @classmethod
    def from_jena_query(cls, query, sparqlop):
        """Create a QueryResult from a Jena/Fuseki query result

        :param dict query: dict extracted from the JSON provided by a query
        :return: a QueryResult instance
        """
        result = QueryResult()
        if 'message' in query:
            result.message = query['message']
        if sparqlop is SPARQLOP.SELECT:
            if 'results' in query:
                result.values = [
                    {key: line[key]['value'] for key in line}
                    for line in query['results']['bindings']
                ]
        elif sparqlop is SPARQLOP.ASK:
            if 'boolean' in query:
                result.values = query['boolean']
        return result


class OntologyMgr:
    """A manager of the data model instantiated in a Jena system"""

    QRY_TYPE_OP_URL_MAPPING = {
        SPARQLOP.SELECT: 'query',
        SPARQLOP.ASK: 'query',
        SPARQLOP.INSERT: 'update',
        SPARQLOP.UPDATE: 'update',
        SPARQLOP.DELETE: 'update',
    }

    QRY_PREFIX_LIST = '\n'.join(
        ['PREFIX {}:<{}>'.format(p.alias, p.url) for p in PREFIX])

    def __init__(self, base_url):
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        # Create query and update wrapper
        self.wrappers = {op: sprqlw.SPARQLWrapper(''.join((self.base_url, op)))
                         for op in ('query', 'update')}

    def _get_wrapper(self, sparqlop):
        """Return SPARQLWrapper corresponding to SPARQL operation"""
        try:
            return self.wrappers[self.QRY_TYPE_OP_URL_MAPPING[sparqlop]]
        except KeyError:
            raise SPARQLError('Invalid SPARQL operator "{}"'.format(sparqlop))

    @staticmethod
    def _query(sparqlw):
        try:
            return sparqlw.query()
        except (
                sprqlw.SPARQLExceptions.SPARQLWrapperException,
                urllib.error.URLError
        ) as exc:
            logger.error('Error while executing SPARQL query: %s\nQuery:\n%s',
                         exc, sparqlw.queryString)
            raise SPARQLError(exc)

    def perform(self, sparqlop, query):
        """Perform SPARQL query

        :param SPARQLOP sparqlop: SPARQL operator
        :param str query: SPARQL query
        :return: A QueryResult instance
        """
        sparqlw = self._get_wrapper(sparqlop)
        query = '{}\n{}'.format(self.QRY_PREFIX_LIST, query)
        sparqlw.setQuery(query)
        if sparqlop is SPARQLOP.SELECT or sparqlop is SPARQLOP.ASK:
            sparqlw.setReturnFormat(sprqlw.JSON)
            result = QueryResult.from_jena_query(
                self._query(sparqlw).convert(), sparqlop)
        else:
            sparqlw.setMethod('POST')
            query_response = self._query(sparqlw)
            result = QueryResult(query_response.response.status,
                                 message=query_response.response.reason)
        return result


class OntologyMgrFactory:
    """Factory class producing OntologyMgr instances"""

    def __init__(self):
        self.base_url = None

    def open(self, url):
        """Set base URL"""
        self.base_url = url

    def close(self):
        """Unset base URL"""
        self.base_url = None

    def get_ontology_manager(self):
        """Produce an OntologyMgr instance"""
        if self.base_url is None:
            raise RuntimeError('OntologyMgrFactory is not initialized')
        return OntologyMgr(self.base_url)


ontology_manager_factory = OntologyMgrFactory()
