"""Serialize/deserialize Space into the data storage"""

from .ontology.generic import ThingDB
from .ontology.manager import PREFIX
from .schemas import ServiceSchema
from .utils import str_insert, str_filter, str_filter_relation, create_filter


class ServiceDB(ThingDB):
    """A class to handle services in the data storage solution"""

    # Dictionary for direct relations - values
    FIELD_TO_RELATION = {
        'id': PREFIX.SERVICES.alias_uri('id'),
        'description': PREFIX.HYDRA.alias_uri('description'),
        'name': PREFIX.HYDRA.alias_uri('title'),
        'url': PREFIX.HYDRA.alias_uri('entrypoint'),
        'has_frontend': PREFIX.SERVICES.alias_uri('hasFrontend'),
    }

    # Dictionaries for attributes that require access to additional
    # concepts/instances
    LINKS = {
        'model_ids': PREFIX.SERVICES.alias_uri('usesModel'),
        'site_ids': PREFIX.SERVICES.alias_uri('installedOn'),
    }

    # Check references exist
    REFERENCES = {
        'model_ids': [PREFIX.SERVICES.alias_uri('Model')],
        'site_ids': [PREFIX.IFC2x3.alias_uri('IfcSite')],
    }

    FILTERS_REF = {
        "site": "?URI {rel} {prefix}:{{id}}\n".format(
            rel=LINKS['site_ids'], prefix=PREFIX.ROOT.alias)
    }

    SCHEMA = ServiceSchema

    def _str_select(self, field, optional=False, dict_=None):
        """Build select line

        :param str field: Field name
        :param bool optional: Whether the field is optional (defaults to False)
        """
        dico = dict_ or self.FIELD_TO_RELATION
        return self._build_select_line(field, dico[field], optional=optional)

    def _build_filter(self, identifier, **filters):
        '''Build a string to add filtering parameters to a SPARQL query
        :param filters dict: a dictionary of parameter names, values
        :return a string to be inserted in the query'''
        filter_str = str_filter_relation(filters, self.FILTERS_REF)

        filters_by_value = {k: filters[k] for k in self.FIELD_TO_RELATION
                            if k in filters and k != "has_frontend"}
        if identifier:
            filters_by_value['id'] = str(identifier)
        if 'kind' in filters:
            filters_by_value['kind'] = filters['kind']
        filter_str += str_filter(filters_by_value)

        if "has_frontend" in filters:
            filter_str += create_filter(
                'has_frontend', filters['has_frontend'])

        return filter_str

    def _build_select_query(self, identifier=None, **filters):
        """A method to build the select query
        :return string: a string for the SPARQL query"""
        _select = [
            """SELECT ?URI ?kind
                (group_concat(distinct ?model; separator=',') as ?model_ids)
                (group_concat(distinct ?site; separator=',') as ?site_ids)"""
            ] + list(self.FIELD_TO_RELATION.keys())
        select = ' ?'.join(_select)
        query = """{sel} WHERE {{
                           ?kind_cls rdfs:subClassOf* {clss}.
                           ?URI a ?kind_cls.
                           ?kind_cls rdfs:label ?kind.
                """.format(sel=select,
                           clss=PREFIX.SERVICES.alias_uri('Service'),)
        query += self._str_select("id")
        query += self._str_select("description", optional=True)
        query += self._str_select("name")
        query += self._str_select("has_frontend")
        query += self._str_select("url", optional=True)
        # get references
        query += "OPTIONAL {{?URI {rel} ?model}}.\n".format(
            rel=self.LINKS['model_ids'])
        query += "OPTIONAL {{?URI {rel} ?site}}.\n".format(
            rel=self.LINKS['site_ids'])
        # add filters
        query += self._build_filter(identifier, **filters)
        query += "}}\n group by ?URI ?kind ?{}".format(
            " ?".join(list(self.FIELD_TO_RELATION.keys())))
        return query

    def _pre_load_binding(self, binding):
        if 'URI' in binding:
            binding.pop('URI')
        # parse multiple references
        binding['model_ids'] = list(map(
            PREFIX.get_name,
            filter(lambda x: x != '',
                   binding.pop('model_ids', '').split(','))))
        binding['site_ids'] = list(map(
            PREFIX.get_name,
            filter(lambda x: x != '',
                   binding.pop('site_ids', '').split(','))))

    def _post_get(self, values):
        return (r for r in values if 'id' in r)

    def _build_create_query(self, _id, element):
        _class = PREFIX.SERVICES.alias_uri(element.kind or 'Service')
        # Build the query
        query = """{{{0} a {1}; {2} "{3}" ;""".format(
            PREFIX.ROOT.alias_uri(_id), _class,
            self.FIELD_TO_RELATION['id'], _id)
        query += self._str_insert(element, "name")
        query += self._str_insert(element, "description", optional=True)
        query += self._str_insert(element, "url", optional=True)
        query += self._str_insert(element, "has_frontend")
        # add references
        for site_id in element.site_ids:
            query += "{rel} {pref}:{id};".format(
                rel=self.LINKS['site_ids'], pref=PREFIX.ROOT.alias,
                id=site_id)
        query += "}"
        return query

    def _str_insert(self, obj, attr, optional=False, final=False):
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
        dict_ = self.FIELD_TO_RELATION
        return str_insert(dict_, obj, attr, optional=optional, final=final)

    def _get_delete_for_update(self, uri):
        """Build the delete query. This method is specific to every object.

        :param uri string: the URI of the object to be removed.
        :return string, string: a SPARQL DELETE clause, and WHERE clause
        """
        to_remove = list(self.FIELD_TO_RELATION.values())
        # to_remove.extend([self.LINKS['localization'], self.LINKS['system']])
        return self._build_remove(uri, to_remove)
