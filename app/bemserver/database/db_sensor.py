"""Serialize/deserialize Space into the data storage"""

from .ontology.generic import ThingDB
from .ontology.manager import PREFIX
from .schemas import SensorSchema
from .utils import str_insert, insert_line, str_filter, str_filter_relation


class SensorDB(ThingDB):
    """A class to handle buildings in the data storage solution"""

    FIELD_TO_RELATION = {
        'id': PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
        'name': PREFIX.IFC2x3.alias_uri('name_IfcRoot'),
        'description': PREFIX.IFC2x3.alias_uri('description_IfcRoot'),
        'static': PREFIX.BUILDING_INFRA.alias_uri('isStatic'),
    }

    LINKS = {
        "localization": PREFIX.BUILDING_INFRA.alias_uri('isLocatedIn'),
        "system_id": PREFIX.BUILDING_INFRA.alias_uri('controls'),
        "measures": PREFIX.SOSA.alias_uri('madeObservation'),
    }
    LINK_REV = {
        "measures": PREFIX.SOSA.alias_uri('madeBySensor'),
    }

    REFERENCES = {
        "site_id": PREFIX.IFC2x3.alias_uri('IfcSite'),
        "building_id": PREFIX.IFC2x3.alias_uri('IfcBuilding'),
        "floor_id": PREFIX.IFC2x3.alias_uri('IfcBuildingStorey'),
        "space_id": PREFIX.IFC2x3.alias_uri('IfcSpace'),
        "system_id": PREFIX.ONTO_MG.alias_uri('Branch'),
        "measures": [PREFIX.SOSA.alias_uri('Observation')],
    }

    FIELD_LOCALIZATION = ['site_id', 'building_id', 'floor_id', 'space_id']

    FIELD_TO_REL_CPLX = {
        'site_id':
            """?URI {rel} ?site. ?site {rel_id} ?site_id.
               FILTER EXISTS {{?site_cls rdfs:subClassOf* {type}.
               ?site a ?site_cls}}.\n""".format(
                   type=REFERENCES['site_id'],
                   rel_id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                   rel=LINKS['localization']),
        'building_id':
            """OPTIONAL {{?URI {rel} ?building.
               ?building {rel_id} ?building_id.
               FILTER EXISTS {{?building_cls rdfs:subClassOf* {type}.
               ?building a ?building_cls}}}}.\n""".format(
                   type=REFERENCES['building_id'],
                   rel_id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                   rel=LINKS['localization']),
        'floor_id':
            """OPTIONAL {{?URI {rel} ?floor.
               ?floor {rel_id} ?floor_id.
               FILTER EXISTS {{?floor_cls rdfs:subClassOf* {type}.
               ?floor a ?floor_cls}}}}.\n""".format(
                   type=REFERENCES['floor_id'],
                   rel_id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                   rel=LINKS['localization']),
        'space_id':
            """OPTIONAL {{?URI {rel} ?space.
               ?space {rel_id} ?space_id.
               FILTER EXISTS {{?space_cls rdfs:subClassOf* {type}.
               ?space a ?space_cls}}}}.\n""".format(
                   type=REFERENCES['space_id'],
                   rel_id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                   rel=LINKS['localization']),
        'system_id':
            '''OPTIONAL {{?URI {rel} ?system.
               ?system {sys_id} ?system_id}}.\n'''.format(
                   rel=LINKS['system_id'],
                   sys_id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot')),
    }

    FILTERS = {
        'system_type':
            """OPTIONAL(?URI {rel} ?sys.\n?sys a ?sys_class.\n
               ?sys_class rdfs:subClassOf* {prefix}:{{val}}).\n""".format(
                   rel=LINKS['system_id'], prefix=PREFIX.IFC2x3.alias),
        # 'measures' : '',
    }

    SCHEMA = SensorSchema

    # FILTERS_REF = {
    #     k:'?URI {rel} {prefix}:{{id}}\n'.format(
    #         rel=LINKS['localization']\
    #             if k in FIELD_LOCALIZATION else LINKS[k],
    #             else LINKS[k],
    #         prefix=PREFIX.ROOT.alias) for k in REFERENCES}

    def _get_filters_ref(self):
        return {
            k: '?URI {rel} {prefix}:{{id}}\n'.format(
                rel=(self.LINKS['localization']
                     if k in self.FIELD_LOCALIZATION else self.LINKS[k]),
                prefix=PREFIX.ROOT.alias) for k in self.REFERENCES}

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
        _select = [
            '''SELECT ?URI
            (group_concat(distinct ?measure; separator=',') as ?measures)'''
            ] +\
            list(self.FIELD_TO_RELATION.keys()) +\
            list(self.FIELD_TO_REL_CPLX.keys())
        select = ' ?'.join(_select)
        query = """{sel} WHERE {{
                           ?cls rdfs:subClassOf* {clss}.
                           ?URI a ?cls.
                """.format(sel=select, clss=PREFIX.SOSA.alias_uri('Sensor'),)
        if identifier is not None:
            query += """?URI {} "{}".\n""".format(
                self.FIELD_TO_RELATION["id"], str(identifier))
        query += self._str_select("id")
        query += self._str_select("name")
        query += self._str_select("description", optional=True)
        query += self._str_select("static")
        # get complex relation
        for attr_name in self.FIELD_TO_REL_CPLX:
            query += self.FIELD_TO_REL_CPLX[attr_name]
        # get measures
        query += "OPTIONAL {{?measure {rel} ?URI}}.\n".format(
            rel=self.LINK_REV['measures'])
        # add filters
        query += self._build_filters(**filters)
        query += "}}\n group by ?URI ?{} ?{}".format(
            " ?".join(list(self.FIELD_TO_RELATION.keys())),
            " ?".join(list(self.FIELD_TO_REL_CPLX.keys())))
        return query

    def _build_filters(self, **filters):
        filters, filter_str = super().str_filter_parent(**filters)
        for filter_ in self.FILTERS:
            value = filters.pop(filter_, None)
            filter_str += self.FILTERS[filter_] if value else ''
        # add filter by specific values: name...
        filter_str += str_filter(
            {x: filters[x] for x in filters if x not in self.REFERENCES})
        filter_str += str_filter_relation(filters, self._get_filters_ref())
        return filter_str

    def _pre_load_binding(self, binding):
        # uri = PREFIX.ROOT.alias_uri(binding['id'])
        # Get localization
        binding['localization'] = {
            k: binding.pop(k, None) for k in self.FIELD_LOCALIZATION}
        # get measures
        # parse multiple references
        binding['measures'] = list(map(
            PREFIX.get_name,
            filter(lambda x: x != '',
                   binding.pop('measures', '').split(','))))

    def _post_get(self, values):
        return (r for r in values if 'id' in r)

    def _build_create_query(self, _id, element):
        _class = PREFIX.SOSA.alias_uri('Sensor')
        # Build the query
        query = """{{
                {0} a {1};
                    {2} "{3}" ;
                """.format(PREFIX.ROOT.alias_uri(_id),
                           _class,
                           PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                           _id)
        # add references to Localization
        for attr_name in self.FIELD_LOCALIZATION:
            query += self._insert_reference(
                element.localization, attr_name, 'localization')
        # add reference to system_id
        query += self._insert_reference(element, 'system_id', 'system_id')
        # add references to measures if they exist
        query += self._insert_reference(element, 'measures', 'measures',
                                        multiple=True)
        query += self._str_insert(element, "description", optional=True)
        query += self._str_insert(element, "static")
        query += self._str_insert(element, "name", final=True)
        query += "}"
        return query

    def _insert_reference(self, object_, attr_name, key_ref, optional=True,
                          multiple=False):
        '''Create a line to for the creation of relation between the current
        sensor and an external element.

        :param object_ Object: the object on which the value is to be obtained
        :param attr_name String:
            the attibute name on object_. Provides the reference
        :param key_ref String: the entry in the LINKS map, to obtain the
            correct relation to create
        :param optional Boolean: True if no error needs to be raised when no
            reference was found
        :param multiple Boolean: True if the attribute is an iterable of
            multiple references
        :returns String: the line to be used in the SPARQL query'''
        elt_id = getattr(object_, attr_name, None)
        if not multiple:
            return insert_line(
                self.LINKS[key_ref], str(elt_id) if elt_id else None,
                prefix=PREFIX.ROOT, optional=optional)
        str_ = '\n'.join(
            [insert_line(self.LINKS[key_ref], str(_id), prefix=PREFIX.ROOT,
                         optional=optional)
             for _id in elt_id])
        return str_

    # def create(self, element):
    #     _id = super().create(element)
    #     my_uri = PREFIX.ROOT.alias_uri(_id)
    #     # Add links with system
    #     # if element.system_id:
    #     #     self._create_relation_to(
    #     #         my_uri, self.LINKS['system'],
    #     #         PREFIX.ROOT.alias_uri(element.system))
    #     # # Add links with measures
    #     # for measure in element.measures:
    #     #     self._create_relation_to(
    #     #         my_uri, self.LINKS['measures'],
    #     #         PREFIX.ROOT.alias_uri(measure))
    #     return _id

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
        return str_insert(
            self.FIELD_TO_RELATION, obj, attr, optional=optional, final=final)

    def _get_delete_for_update(self, uri):
        """Build the delete query. This method is specific to every object.

        :param uri string: the URI of the object to be removed.
        :return string, string: a SPARQL DELETE clause, and WHERE clause
        """
        to_remove = list(self.FIELD_TO_RELATION.values())
        to_remove.extend([self.LINKS['localization'], self.LINKS['system_id']])
        return self._build_remove(uri, to_remove)

    # def update(self, identifier, new_element):
    #     """Update the element identified by its ID - replace it with the
    #     element new_element
    #
    #     :param identifier identifier: a unique id for element to be updated
    #     :param new_element Thing: the new elements that should replace the
    #         one identified by identifier
    #     """
    #     super().update(identifier, new_element)
    #     my_uri = PREFIX.ROOT.alias_uri(identifier)
    #     # Add relation with parent
    #     #self._remove_relation(my_uri, self.LINKS['localization'])
    #     # Add links with system
    #     # if new_element.system_id:
    #     #     self._create_relation_to(
    #     #         my_uri, self.LINKS['system_id'],
    #     #         PREFIX.ROOT.alias_uri(new_element.system_id))
