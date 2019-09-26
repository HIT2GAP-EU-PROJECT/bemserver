"""Serialize/deserialize Space into the data storage"""

from ..models import Space, SpaceOccupancy, SpatialInfo
from .ontology.generic import StructuralElementDB
from .ontology.manager import PREFIX
from .schemas import SpaceSchema
from .utils import str_insert, str_filter, str_filter_relation


class SpaceDB(StructuralElementDB):
    """A class to handle buildings in the data storage solution"""

    FIELD_TO_RELATION = {
        'id': PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
        'name': PREFIX.IFC2x3.alias_uri('name_IfcRoot'),
        'description': PREFIX.IFC2x3.alias_uri('description_IfcRoot'),
    }

    FIELD_TO_REL_CPLX = {
        "floor_id": "?URI {rel} ?floor. ?floor {id} ?floor_id.".format(
            rel=PREFIX.BUILDING_INFRA.alias_uri('isContainedIn'),
            id=FIELD_TO_RELATION['id'])
    }

    LINKS = {
        "parent": PREFIX.BUILDING_INFRA.alias_uri('contains'),
    }

    OCCUPANCY = {
        'nb_max': PREFIX.PROPERTY.alias_uri('MaxOccupancy'),
        'nb_permanents': PREFIX.PROPERTY.alias_uri('PermanentOccupancy'),
    }

    CLASS_TO_FIELD_TO_RELATION = {
        Space: FIELD_TO_RELATION,
        SpaceOccupancy: OCCUPANCY,
    }

    REFERENCES = {
        'floor_id': PREFIX.BUILDING_INFRA.alias_uri('Floor'),
    }

    FILTER_REF = {
        'kind': """VALUES ?cls_str {{{{'{{id}}' '{{id}}'@en }}}}.
           ?cls {rel} ?kind_cls.
           ?kind_cls {rel_name} ?cls_str.""".format(
               rel=PREFIX.RDFS.alias_uri('subClassOf*'),
               rel_name=PREFIX.RDFS.alias_uri('label')),
    }

    SCHEMA = SpaceSchema

    def _str_select(self, obj_class, field, optional=False):
        '''Build a select line

        :param obj_class: Thing class
        :param str field: Field name
        :param bool optional: whether the field is optional
            (default to False)'''
        return self._build_select_line(
            field, self.CLASS_TO_FIELD_TO_RELATION[obj_class][field],
            optional=optional)

    def _build_select_query(self, identifier=None, **filters):
        """A method to build the select query
        :return string: a string for the SPARQL query"""
        _select = ["SELECT ?URI ?kind ?nb_max ?nb_permanents"] +\
            list(self.FIELD_TO_RELATION.keys()) +\
            list(self.FIELD_TO_REL_CPLX.keys())
        select = ' ?'.join(_select)
        query = """{sel} WHERE {{
                           ?cls rdfs:subClassOf* {clss}.
                           ?URI a ?cls.
                           ?cls {kind} ?kind.
                """.format(sel=select,
                           clss=PREFIX.IFC2x3.alias_uri('IfcSpace'),
                           kind=PREFIX.RDFS.alias_uri('label'))
        if identifier is not None:
            query += """?URI {} "{}".\n""".format(
                self.FIELD_TO_RELATION["id"],
                str(identifier))
        query += self._str_select(Space, "id")
        query += self._str_select(Space, "name")
        query += self._str_select(SpaceOccupancy, "nb_max", optional=True)
        query += self._str_select(SpaceOccupancy, "nb_permanents",
                                  optional=True)
        query += self._str_select(Space, "description", optional=True)
        query += self.FIELD_TO_REL_CPLX['floor_id']
        # handle filter
        query += self._build_filters(**filters)
        query += "}"
        return query

    def _build_filters(self, **filters):
        '''Build the string for filtering'''
        filters, filter_str = super().str_filter_parent(**filters)
        filter_str += str_filter_relation(filters, self.FILTER_REF)
        for key in self.FILTER_REF:
            filters.pop(key, None)
        return filter_str + str_filter(filters)

    def _pre_load_binding(self, binding):
        binding['spatial_info'] = self._create_spatial_info_binding(
            SpatialInfo,
            PREFIX.ROOT.alias_uri(PREFIX.get_name(binding['URI'])))
        # Add quantities
        occupancy_keys = ('nb_max', 'nb_permanents')
        occupancy = {
            key: binding.pop(key, None) for key in occupancy_keys
            if key in binding}
        if occupancy:
            binding['occupancy'] = occupancy

    def _build_create_query(self, _id, element):
        if element.kind is not None:
            _class = PREFIX.BUILDING_INFRA.alias_uri(element.kind)
        else:
            _class = PREFIX.IFC2x3.alias_uri('IfcSpace')
        # Build the query
        query = """{{
                {0} a {1};
                    {2} "{3}" ;
                """.format(PREFIX.ROOT.alias_uri(_id),
                           _class,
                           PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                           _id)
        if element.occupancy:
            query += self._str_insert(
                element.occupancy, "nb_max", optional=True)
            query += self._str_insert(
                element.occupancy, "nb_permanents", optional=True)
        query += self._str_insert(element, "description", optional=True)
        query += self._str_insert(element, "name", final=True)
        query += "}"
        return query

    def create(self, element):
        _id = super().create(element)
        # Add relation with parent
        parent_uri = PREFIX.ROOT.alias_uri(element.floor_id)
        my_uri = PREFIX.ROOT.alias_uri(_id)
        self._create_relation_to(parent_uri, self.LINKS['parent'], my_uri)
        # Create quantities
        self.create_quantities(
            element.spatial_info.get_quantities() if element.spatial_info
            else [], my_uri)
        return _id

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
            self.CLASS_TO_FIELD_TO_RELATION[obj.__class__],
            obj, attr, optional=optional, final=final)

    def _get_delete_for_update(self, uri):
        """Build the delete query. This method is specific to every object.

        :param uri string: the URI of the object to be removed.
        :return string, string: a SPARQL DELETE clause, and WHERE clause
        """
        rels = list(self.FIELD_TO_RELATION.values())
        rels.extend(list(self.OCCUPANCY.values()))
        return self._build_remove(uri, rels)

    def update(self, identifier, new_element):
        """Update the element identified by its ID - replace it with the
        element new_element

        :param identifier identifier: a unique identifier for the element to be
            updated
        :param new_element Thing: the new elements that should replace the one
            identified by identifier
        """
        super().update(identifier, new_element)
        if new_element.spatial_info:
            self.update_properties(
                identifier, new_element.spatial_info.get_quantities())
