"""Serialize/deserialize Space into the data storage"""

from .ontology.generic import ThingDB
from ..models import OutputEvent
from .ontology.manager import PREFIX
from .schemas import OutputSchema
from .utils import str_insert, str_filter


class OutputDB(ThingDB):
    """Class to handle services outputs in the data model
    Available operations are:
    - add/create an output for a pair application/model
    - get outputs filtered by an application ID, a model ID, a localization,
        a type of output, a type of value (only for an output of type time
        series)
    """

    FIELD_TO_RELATION = {
        # for time series only
        'id': PREFIX.SERVICES.alias_uri('id'),
        'sampling': PREFIX.SERVICES.alias_uri('sampling'),
        'external_id': PREFIX.SERVICES.alias_uri('externalID'),
    }

    LINKS = {
        'module_id': PREFIX.SERVICES.alias_uri('service'),
        'model_id': PREFIX.SERVICES.alias_uri('model'),
        # time series only
        'localization': PREFIX.SERVICES.alias_uri('localization')
    }
    LINKS_ENUMERATE = {
        # for time series only
        'kind': PREFIX.SERVICES.alias_uri('valueType'),
        'unit': PREFIX.SERVICES.alias_uri('valueUnit'),
    }

    REFERENCES = {
        'module_id': PREFIX.SERVICES.alias_uri('Service'),
        'model_id': PREFIX.SERVICES.alias_uri('Model'),
        # for time series only
        'localization': PREFIX.IFC2x3.alias_uri('IfcSpatialElement'),
        # type of output
    }

    REFERENCES_ENUM = {
        'kind': {'prefix': PREFIX.PROPERTY,
                 'type': PREFIX.PROPERTY.alias_uri('Property'),
                 'indiv': False},
        'unit': {'prefix': [PREFIX.UNIT, PREFIX.PROPERTY],
                 'type': PREFIX.QUDT.alias_uri('Unit'),
                 'indiv': True},
    }

    _PARENT = """?URI {rel} ?{cls}. ?{cls} {rel_id} ?{cls}_id.
        FILTER EXISTS {{?{cls}_cls rdfs:subClassOf* {type}.
        ?{cls} a ?{cls}_cls}}.\n"""

    FIELD_TO_REL_CPLX = {
        'module_id': _PARENT.format(
            cls='module', type=REFERENCES['module_id'],
            rel_id=PREFIX.SERVICES.alias_uri('id'), rel=LINKS['module_id']),
        'model_id': _PARENT.format(
            cls='model', type=REFERENCES['model_id'],
            rel_id=PREFIX.SERVICES.alias_uri('id'), rel=LINKS['model_id']),
        'localization': """OPTIONAL {{?URI {rel} ?location.
            ?location {rel_id} ?localization.
            FILTER EXISTS {{?location_cls rdfs:subClassOf* {type}.
            ?location a ?location_cls}}}}.\n""".format(
                type=REFERENCES['localization'],
                rel_id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                rel=LINKS['localization']),
        'kind': """OPTIONAL {{?URI {rel} ?obs_type.
            ?obs_type {rel_id} ?kind.
            FILTER EXISTS
            {{?obs_type_cls rdfs:subClassOf* {type}}}}}.\n""".format(
                type=REFERENCES_ENUM['kind']['type'],
                rel_id=PREFIX.RDFS.alias_uri('label'),
                rel=LINKS_ENUMERATE['kind']),
        'unit': """OPTIONAL{{?URI {rel} ?unit.
            FILTER EXISTS {{?unit_cls rdfs:subClassOf* {type}.
            ?unit a ?unit_cls}}}}.\n""".format(
                type=REFERENCES_ENUM['unit']['type'],
                rel=LINKS_ENUMERATE['unit']),
    }

    SCHEMA = OutputSchema

    def _build_filter(self, identifier, **filters):
        '''Build a string to add filtering parameters to a SPARQL query
        :param filters dict: a dictionary of parameter names, values
        :return a string to be inserted in the query'''
        filter_str = ''
        filters_by_value = {}
        # changer filters keys
        if 'kind' in filters:
            filters_by_value['cls'] = filters.pop('kind')
        if 'value_type' in filters:
            filters_by_value['kind'] = filters.pop('value_type')
        for _dict in [self.FIELD_TO_RELATION, self.REFERENCES_ENUM,
                      self.REFERENCES]:
            filters_by_value.update({k: filters[k] for k in _dict
                                     if k in filters})
        if identifier:
            filters_by_value['id'] = str(identifier)
        filter_str += str_filter(filters_by_value)
        return filter_str

    def _str_select(self, field, optional=False, dict_=None):
        """Build select line

        :param str field: Field name
        :param bool optional: Whether the field is optional (defaults to False)
        """
        dico = dict_ or self.FIELD_TO_RELATION
        return self._build_select_line(field, dico[field], optional=optional)

    def _build_select_query(self, identifier=None, **filters):
        """A method to build the select query
        :return string: a string for the SPARQL query"""
        _select = ["SELECT ?URI ?cls"] + \
            list(self.FIELD_TO_RELATION.keys()) + list(self.FIELD_TO_REL_CPLX)
        select = ' ?'.join(_select)
        query = """{sel} WHERE {{
                           ?cls rdfs:subClassOf* {clss}.
                           ?URI a ?cls.
                """.format(sel=select,
                           clss=PREFIX.SERVICES.alias_uri('Output'),)
        query += self._str_select("id")
        query += self._str_select("sampling", optional=True)
        query += self._str_select("external_id", optional=True)
        # get references
        for attr_ in self.FIELD_TO_REL_CPLX:
            query += self.FIELD_TO_REL_CPLX[attr_]
        # add filters
        query += self._build_filter(identifier, **filters)
        query += "}"
        return query

    def _pre_load_binding(self, binding):
        binding['cls'] = PREFIX.get_name(binding['cls'])
        if binding['cls'] == 'TimeSeries':
            binding['values_desc'] = {
                k: binding.pop(k)
                for k in ['kind', 'sampling'] if k in binding}
            if 'unit' in binding:
                binding['values_desc']['unit'] = PREFIX.get_name(
                    binding.pop('unit'))

# ######### INSERT #################

    def _str_insert(self, obj, attr, dico=None, optional=False, final=False,
                    prefix=None):
        """Build up the line corresponding to an object attribute, into
        a SPARQL insert method, in the form "relation value". Value is
        extracted from obj.attr, the relation is extracted from a dictionary.

        :subj String: the subject of the triple to be created
        :obj Object: an object
        :attr String: the name of the attribute
        :optional boolean: True if the element to be inserted is optional
        :return: a String to be inserted into the INSERT query, of the form
            rel value
        """
        dict_ = dico or self.FIELD_TO_RELATION
        attr_ = attr if not prefix else prefix.alias_uri(attr)
        return str_insert(dict_, obj, attr_, optional=optional, final=final)

    def _build_create_query(self, _id, element):
        is_event = isinstance(element, OutputEvent)
        _class = PREFIX.SERVICES.alias_uri('Event' if is_event
                                           else 'TimeSeries')
        # Build the query
        query = ["""{{{0} a {1}; {2} "{3}";""".format(
            PREFIX.ROOT.alias_uri(_id), _class,
            self.FIELD_TO_RELATION['id'], _id)]
        query.append("{rel} {obj};".format(
            rel=self.LINKS['module_id'],
            obj=PREFIX.ROOT.alias_uri(element.module_id)))
        query.append("{rel} {obj};".format(
            rel=self.LINKS['model_id'],
            obj=PREFIX.ROOT.alias_uri(element.model_id)))
        if is_event:
            return "".join(query + ["}"])
        query.append(
            self._str_insert(element.values_desc, "sampling", optional=True))
        query.append(self._str_insert(element, "external_id", optional=True))
        # add references
        query.append("{rel} {obj};".format(
            rel=self.LINKS['localization'],
            obj=PREFIX.ROOT.alias_uri(element.localization)))
        for prefix in self.REFERENCES_ENUM['unit']['prefix']:
            if self._check_exists(
                    element.values_desc.unit,
                    self.REFERENCES_ENUM['unit']['type'], prefix, True):
                query += "{rel} {pref}:{id};".format(
                    rel=self.LINKS_ENUMERATE['unit'], pref=prefix.alias,
                    id=element.values_desc.unit)
                break
        query.append("{rel} {obj};".format(
            rel=self.LINKS_ENUMERATE['kind'],
            obj=PREFIX.PROPERTY.alias_uri(element.values_desc.kind)))
        return "".join(query + ["}"])

    def _get_delete_for_update(self, uri):
        """Build the delete query. This method is specific to every object.

        :param uri string: the URI of the object to be removed.
        :return string, string: a SPARQL DELETE clause, and WHERE clause
        """
        to_remove = list(self.FIELD_TO_RELATION.values()) +\
            list(self.LINKS_ENUMERATE.values())
        to_remove.extend([self.LINKS['localization']])
        return self._build_remove(uri, to_remove)
