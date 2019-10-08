"""Abstract database accessor classes

Provides facilities for querying database and non-duplication of data
"""

import abc

from marshmallow import ValidationError

from .manager import PREFIX, SPARQLOP, ontology_manager_factory
from ..db_quantity import QuantityDB
from ..utils import generate_id
from ..exceptions import ItemNotFoundError, ItemError


class ThingDB(abc.ABC):
    """An interface for Data Access Object Pattern realization"""

    # References.
    # keys: attributes in model object
    # values: types PREFIX.IFC2x3.alias_uri('IfcBuilding')
    # By convention, if the attribute is plural, put type in a list
    # E.g.:
    # REFERENCES = {
    #     'building': PREFIX.IFC2x3.alias_uri('IfcBuilding'),  # singular
    #     'spaces': [PREFIX.IFC2x3.alias_uri('IfcSpace')],     # plural
    # }
    REFERENCES = {}
    REFERENCES_ENUM = {}

    FILTER_PARENT = """?URI {rel} ?parent_site.
        FILTER (?parent_site IN {{set}}).""".format(
            rel=PREFIX.BUILDING_INFRA.alias_uri('parentSite'))
    SCHEMA = None

    def __init__(self):
        self.onto_mgr = ontology_manager_factory.get_ontology_manager()

    def str_filter_parent(self, **filters):
        '''builds a string to filter by parent site
        :param site_ids List: the filters passed to the query.
        :return String: the filtering string to be inserted in the query'''
        site_ids = filters.pop('sites', None)
        if not site_ids:
            return filters, ''
        sites = '({})'.format(
            ','.join([PREFIX.ROOT.alias_uri(site_id) for site_id in site_ids]))
        return filters, self.FILTER_PARENT.format(set=sites)

    @staticmethod
    def _build_select_line(field, relation, optional=False):
        """Get SPARQL codes for a select based on field name and the objects

        :param str field: Field name
        :param str relation: Relation (URI)
        :param bool optional: Whether the field is optional (defaults to False)
        """
        result = "?URI {} ?{}".format(relation, field)
        if optional:
            result = 'OPTIONAL {{{}}}'.format(result)
        return result + ".\n"

    @abc.abstractmethod
    def _build_select_query(self, identifier=None, **filters):
        """Build the select query

        @return string: SPARQL query
        """

    def _add_filters_to_binding(self, binding, **filters):
        for filter_name in self.FILTERS:
            if filter_name in filters:
                binding[filter_name] = filters[filter_name]
        return binding

    def _to_object(self, binding):
        """Build Thing instance from SPARQL query binding

        :param dict binding: Element of QueryResult.result
        :return Thing: Thing instance
        """
        self._pre_load_binding(binding)
        return self.SCHEMA().load(binding).data

    def _pre_load_binding(self, binding):
        """Mutate binding to prepare loading by object Schema

        :param dict binding: Element of QueryResult.result
        """

    def _get(self, identifier=None, **filters):
        """Get elements. Request can be filtered by identifier

        :param str identifier: identifier of the element to request
        :return: Generator of Thing instances
        """
        query = self._build_select_query(identifier=identifier, **filters)
        result = self.onto_mgr.perform(SPARQLOP.SELECT, query)
        values = self._post_get(result.values)
        return (self._to_object(bind) for bind in values)

    def _post_get(self, values):
        """Override to filter query results in child class"""
        return values

    def get_all(self, **filters):
        """Get the list of all elements in a project"""
        return self._get(identifier=None, **filters)

    def get_by_id(self, identifier, **filters):
        """Get an element from its id

        :param str identifier: identifier of the element to request
        """
        try:
            return next(self._get(identifier=identifier, **filters))
        except StopIteration:
            raise ItemNotFoundError

    def _build_filters(self, optional=False, **filters):
        '''Create filters for a query
        :param optional boolean: True if the value are to be taken in the
            FILTERS_OPT dictionary; otherwise in FILTERS
        :param filters Dictionnary: a dictionary of kay, values to be used'''
        _filters = self.FILTERS_OPT if optional else self.FILTERS
        if not optional:
            fun = lambda x: _filters[x].format(
                val="'{}'".format(filters[x]) if x in filters
                else "?{}".format(x))
        else:
            fun = lambda x: _filters[x].format(
                val="{}".format(filters[x])) if x in filters else None
        filters_v = list(
            filter(lambda x: x is not None, [fun(v) for v in _filters]))
        return ''.join(filters_v) if filters_v else ''

    def create(self, element):
        """Create an element. Element is assigned an ID at creation.

        :param Thing element: Element object to be created
        :return: Created element ID
        """
        self._validate_refs(element)
        _id = generate_id()
        query = self._build_create_query(_id, element)
        self.onto_mgr.perform(SPARQLOP.INSERT, 'INSERT DATA {}'.format(query))
        element.id = _id
        return _id

    def _validate_refs(self, element):
        """Validate type and existence of references

        This is meant to be called before create/update operations.
        """
        errors = {}
        for attr, _type in self.REFERENCES.items():
            errors.update(self._validate_single_ref(element, attr, _type))
        for attr, pties in self.REFERENCES_ENUM.items():
            errors.update(self._validate_single_ref(
                element, attr, pties['type'], pties['prefix'], pties['indiv']))
        if errors:
            raise ValidationError(errors)

    def _validate_single_ref(
            self, element, attr, _type, prefix=None, indiv=True):
        prefixes = [prefix] if not isinstance(prefix, list) else prefix
        errors = {}
        for _prefix in prefixes:
            errors = self._validate_single_ref_single_type(
                element, attr, _type, _prefix, indiv)
            if len(errors) == 0:
                return errors
        return errors

    def _validate_single_ref_single_type(
            self, element, attr, _type, prefix, indiv):
        """Validate a reference"""
        errors = {}
        if not isinstance(_type, list):
            _id = getattr(element, attr, None)
            if _id is not None:
                if not self._check_exists(_id, _type, prefix, indiv):
                    errors[attr] = ['Reference not found', ]
        else:
            _id_list = getattr(element, attr, [])
            for idx, _id in enumerate(_id_list):
                if not self._check_exists(_id, _type[0], prefix, indiv):
                    errors.setdefault(attr, {})
                    errors[attr][str(idx)] = ['Reference not found', ]
        return errors

    def _check_exists(self, _id, _type, prefix, individuals):
        """Check existence and type of an element

        :param str _id: UUID of the element
        :param str _type: alias URI of the element type
        :param prefix: the prefix used to build the URI of the element
        :param bool individuals: True if the element is supposed to be an
            individual
        """
        uri = PREFIX.ROOT.alias_uri(_id) if not prefix\
            else prefix.alias_uri(_id)
        param_query = "ASK WHERE {{?c {rel}* {type}. {uri} a ?c}}"\
            if individuals else "ASK WHERE {{{uri} {rel}* {type}}}"
        query = param_query.format(
            rel=PREFIX.RDFS.alias_uri('subClassOf'), type=_type, uri=uri)
        result = self.onto_mgr.perform(SPARQLOP.ASK, query)
        return result.values

    @abc.abstractmethod
    def _build_create_query(self, _id, element):
        """Build query to add element to the ontology

        @element: element to add
        """

    def remove(self, identifier):
        """Remove an element identified by its id

        :param UUID identifier: identifier of the element to remove
        """
        delete, where = self._build_remove(PREFIX.ROOT.alias_uri(identifier))
        self.onto_mgr.perform(SPARQLOP.DELETE, "{} {}".format(delete, where))

    @abc.abstractmethod
    def _get_delete_for_update(self, uri):
        """Method to build the delete part of a DELETE/INSERT operation.

        This method is specific to every object.
        :param uri string: the URI of the object to be removed.
        :param all boolean: true if all links for this object should be
            removed.
        :return string, string: a SPARQL DELETE clause, and WHERE clause
        """

    def _build_remove(self, uri, relations=None):
        """Build a delete query based on the relation to be removed for
        the considered URI.

        :param uri String: the URI of the object that needs deletion
        :param relations List: a list of strings, each string being a relation
            in the model
        :param all boolean: True if all relations need to be removed.
        :return: A tuple of strings: the delete and query clauses
        """
        body = ""
        if relations is not None:
            # ensure the class is also removed
            body = "{} a ?v.\n".format(uri)
            for rel in relations:
                body += "{} {} ?v.\n".format(uri, rel)
        else:
            body = "{} ?p ?v.".format(uri)
        return "DELETE {{{}}}".format(body), "WHERE {{{} ?p ?v.}}".format(uri)

    def update(self, identifier, new_element):
        """Replace element identified by ID with new_element

        :param UUID identifier: unique identifier of the element to update
        :param Thing new_element: new element that should replace the one
            identified by identifier
        """
        self._validate_refs(new_element)
        delete, where = self._get_delete_for_update(
            PREFIX.ROOT.alias_uri(identifier))
        insert = self._build_create_query(identifier, new_element)
        self.onto_mgr.perform(
            SPARQLOP.UPDATE, "{} INSERT {} {}".format(delete, insert, where))
        new_element.id = identifier

    def get_related_individuals_id(self, url, relation, parent_cls=None):
        """Get IDs of individuals in the triple <url, relation, ?individuals>

        :param str url: Parent URL
        :param str relation: Relation linking the url
        :param str parent_cls: URL for the class of the individuals
        :return: list of individuals IDs (not the URI)
        """
        if parent_cls:
            filter_ = (
                '?cls {0}* {1}. ?indiv a ?cls'
                .format(PREFIX.RDFS.alias_uri('subClassOf'), parent_cls))
        else:
            filter_ = ''
        query = """SELECT ?indiv WHERE {{
                   {url} {rel} ?indiv.
                   {filt}
                }}""".format(url=url, rel=relation, filt=filter_)
        result = self.onto_mgr.perform(SPARQLOP.SELECT, query)
        return [PREFIX.get_name(indiv['indiv']) for indiv in result.values]

    def _create_relation_to(self, subj, relation, obj):
        """Create a relation between objects

        :param subj: the alias of the subject of the relation.
        :param relation: the alias of the relation.
        :param obj: the alias of the obkect of the relation
        """
        query = "INSERT DATA {{{} {} {}}}".format(subj, relation, obj)
        self.onto_mgr.perform(SPARQLOP.INSERT, query)

    def _remove_relation(self, subj, relation=None):
        """Removes relations with object

        :param subj: the alias of the subject of the relation
        :param relation: alias of the relation. By default all relations
        """
        filter_ = "FILTER (?rel = {}).".format(relation) if relation else ""
        triple = "{} {} ?obj".format(subj, relation or "?obj")
        query = """DELETE {{{}}} WHERE {{
            {} ?rel ?obj. {}}}""".format(triple, subj, filter_)
        self.onto_mgr.perform(SPARQLOP.DELETE, query)

    def _create_spatial_info_binding(self, class_, uri):
        """Create bindings for spatial information associated to a Schema

        :param uri: The URI associated to the object
        :return: Dictionary to create a spatial information"""
        quantities = self.get_quantities_for(
            uri, relation=self.PROPERTIES['properties'])
        return {
            class_.get_attr_name(q.kind): q.value for q in quantities}

    def get_parent(self, my_uuid):
        '''Returns the site ID to which the object identified by my_uuid is
        attached.
        :param my_uuid UUID: the UUID of the current object
        :return a string for the UUID of the parent'''
        uri = PREFIX.ROOT.alias_uri(my_uuid)
        query = "SELECT ?parent_site WHERE {{{uri} {rel} ?parent_site}}"\
            .format(uri=uri, rel=PREFIX.BUILDING_INFRA.alias_uri('parentSite'))
        result = self.onto_mgr.perform(SPARQLOP.SELECT, query)
        if len(result.values) != 1:
            raise ItemError
        return PREFIX.get_name(result.values[0]['parent_site'])


class StructuralElementDB(ThingDB):
    """An abstract class for Structural elements"""

    PROPERTIES = {
        'properties': PREFIX.SSN.alias_uri('hasProperty'),
    }

    def __init__(self):
        super().__init__()
        self.quantity_db = QuantityDB()

    def get_quantities_for(self, elt_uri, relation=None, kind=None):
        """Get the quantities associated to a elt_uri

        :param str elt_uri: URI of the parent element
        :param str relation: Type of relation between the parent element and
            its quantities
        :param str kind: Kind quantities to be used as a filter
        :return: A list of quantities
        """
        return list(self.quantity_db.get_all_for(
            elt_uri, relation=relation, kind=kind))

    def create_quantities(self, quantities, elt_url):
        """Serialize the quantities attached to elt in the data model

        :param list quantities: List of quantity objects
        :param str elt_url: URI of element
        """
        for quantity in quantities:
            self.quantity_db.create_for(
                quantity, self.PROPERTIES['properties'], elt_url)

    def _create_surface_info_binding(self, uri):
        """Create bindings for spatial information associated to a WallSchema

        :param uri: The URI associated to the object
        :param dimensions: A dictionary
        :param properties: The PROPERTIES dictionary of DB handler
        :return: Dictionary to create a spatial information"""
        spatial_binding = {}
        for quantity in self.DIMENSIONS:
            quantities = self.get_quantities_for(
                uri,
                relation=self.PROPERTIES['properties'],
                kind=self.DIMENSIONS[quantity])
            spatial_binding[quantity] = quantities[0].value\
                if len(list(quantities)) == 1 else None
        return spatial_binding

    def remove(self, identifier):
        """Remove an element identified by its id

        :param uuid identifier: identifier of the element to remove
        """
        quantities_uris = self.quantity_db.get_all_uris_for(
            PREFIX.ROOT.alias_uri(identifier),
            relation=self.PROPERTIES['properties'])
        super().remove(identifier)
        for uri in quantities_uris:
            self.quantity_db.remove(uri)

    def update_properties(self, identifier, quantities):
        """Update the properties of the elements identified by identifier. It
        needs first to remove the current quantities and to create new ones

        :param uri string: the URI of the element that has some quantities
        :param quantities: the new quantities to associate to URI
        """
        uri = PREFIX.ROOT.alias_uri(identifier)
        quantity_urls = self.quantity_db.get_all_uris_for(
            uri, relation=self.PROPERTIES['properties'])
        for qurl in quantity_urls:
            self.quantity_db.remove(qurl)
        if quantities:
            self.create_quantities(quantities, uri)
