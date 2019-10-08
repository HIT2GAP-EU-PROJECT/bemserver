"""Serialize/deserialize Floor into the data storage solution"""

from .ontology.generic import StructuralElementDB
from .ontology.manager import PREFIX
from .schemas import FloorSchema
from ..models import SpatialInfo
from .utils import str_insert, str_filter, str_filter_relation


class FloorDB(StructuralElementDB):
    """A class to handle buildings in the data storage solution"""

    FIELD_TO_RELATION = {
        'id': PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
        'name': PREFIX.IFC2x3.alias_uri('name_IfcRoot'),
        'description': PREFIX.IFC2x3.alias_uri('description_IfcRoot'),
        'level': PREFIX.BUILDING_INFRA.alias_uri('floorLevel'),
    }

    FIELD_TO_REL_CPLX = {
        'building_id':
            "?URI {rel} ?building. ?building {id} ?building_id.".format(
                rel=PREFIX.BUILDING_INFRA.alias_uri('isContainedIn'),
                id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'))
    }

    LINKS = {
        'parent': PREFIX.BUILDING_INFRA.alias_uri('contains'),
    }

    REFERENCES = {
        'building_id': PREFIX.IFC2x3.alias_uri('IfcBuilding'),
    }

    FILTER_REF = {
        'kind': """VALUES ?cls_str {{{{'{{id}}' '{{id}}'@en }}}}.
           ?cls {rel} ?kind_cls.
           ?kind_cls {rel_name} ?cls_str.""".format(
               rel=PREFIX.RDFS.alias_uri('subClassOf*'),
               rel_name=PREFIX.RDFS.alias_uri('label')
           ),
    }

    SCHEMA = FloorSchema

    def _str_select(self, field, optional=False):
        """Get SPARQL codes for a select based on field name

        :param str field: Field name
        :param bool optional: Whether the field is optional (defaults to False)
        """
        return self._build_select_line(
            field,
            self.FIELD_TO_RELATION[field],
            optional=optional)

    def _build_select_query(self, identifier=None, **filters):
        """A method to build the select query
        :return string: a string for the SPARQL query"""
        _select = ["SELECT ?URI ?kind"] + \
            list(self.FIELD_TO_RELATION.keys()) + \
            list(self.FIELD_TO_REL_CPLX.keys())
        select = ' ?'.join(_select)
        query = """{sel} WHERE {{
                    ?cls rdfs:subClassOf* {clss}.
                    ?URI a ?cls.
                    ?cls {kind} ?kind.
                """.format(sel=select,
                           clss=PREFIX.BUILDING_INFRA.alias_uri('Floor'),
                           kind=PREFIX.RDFS.alias_uri('label'),)
        # ?kind rdf:label ?cls.
        if identifier is not None:
            query += '?URI {} "{}".\n'.format(
                self.FIELD_TO_RELATION["id"],
                str(identifier))
        query += self._str_select("id")
        query += self._str_select("name")
        query += self._str_select("level")
        query += self._str_select("description", optional=True)
        query += self.FIELD_TO_REL_CPLX['building_id']
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
            SpatialInfo, PREFIX.ROOT.alias_uri(binding['id']))
        # binding['spatial_info'] = quantities

    def _build_create_query(self, _id, element):
        # Build the query
        query = """{{
                {0} a {1};
                    {2} "{3}" ;
                """.format(
                    PREFIX.ROOT.alias_uri(_id),
                    PREFIX.BUILDING_INFRA.alias_uri(element.kind or 'Floor'),
                    PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                    _id)
        query += self._str_insert(element, "level")
        query += self._str_insert(element, "description", optional=True)
        query += self._str_insert(element, "name", final=True)
        query += "}"
        return query

    def create(self, element):
        _id = super().create(element)
        # Add relation with parent
        parent_uri = PREFIX.ROOT.alias_uri(element.building_id)
        my_uri = PREFIX.ROOT.alias_uri(_id)
        self._create_relation_to(parent_uri, self.LINKS['parent'], my_uri)
        # Create quantities
        if element.spatial_info:
            self.create_quantities(
                element.spatial_info.get_quantities(), my_uri)
        return _id

    def _str_insert(self, obj, attr, optional=False, final=False):
        """Build up the line corresponding to an object attribute, into a
        SPARQL insert method, in the form "relation value". Value is extracted
        from obj.attr, the relation is extracted from a dictionary.

        :param subj String: the subject of the triple to be created
        :param obj Object: an object
        :param attr String: the name of the attribute
        :param optional boolean: True if the element to be inserted is optional
        :return: a String to be inserted into the INSERT query, of the form
            rel value
        """
        return str_insert(self.FIELD_TO_RELATION, obj, attr,
                          optional=optional, final=final)

    def _get_delete_for_update(self, uri):
        """Method to build the delete query. This method is specific to every
        object.

        :param uri string: the URI of the object to be removed.
        :return string, string: a SPARQL DELETE clause, and WHERE clause
        """
        rels = list(self.FIELD_TO_RELATION.values())
        return self._build_remove(uri, rels)

    def update(self, identifier, new_element):
        """Update the element identified by its ID - replace it with the element
        new_element

        :param identifier identifier: identifier of the element to update
        :param new_element Thing: the new elements that should replace the one
            identified by identifier
        """
        super().update(identifier, new_element)
        if new_element.spatial_info:
            self.update_properties(
                identifier, new_element.spatial_info.get_quantities())
