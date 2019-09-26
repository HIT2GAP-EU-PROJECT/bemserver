"""Serialize/deserialize Space into the data storage"""

from ..models.facade import Facade
from ..models.spatial import SurfaceInfo
from .ontology.generic import StructuralElementDB
from .ontology.manager import PREFIX
from .schemas import FacadeSchema
from .utils import str_insert, str_filter, str_filter_relation


class FacadeDB(StructuralElementDB):
    """A class to handle buildings in the data storage solution"""

    FIELD_TO_RELATION = {
        'id': PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
        'name': PREFIX.IFC2x3.alias_uri('name_IfcRoot'),
        'description': PREFIX.IFC2x3.alias_uri('description_IfcRoot'),
        'windows_wall_ratio':
            PREFIX.BUILDING_INFRA.alias_uri('windowWallRatio'),
        'interior': PREFIX.BUILDING_INFRA.alias_uri('isInside')
    }

    FIELD_TO_REL_CPLX = {
        "building_id":
            "?URI {rel} ?building. ?building {id} ?building_id.\n".format(
                rel=PREFIX.BUILDING_INFRA.alias_uri('isContainedIn'),
                id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot')),
    }

    LINKS = {
        "windows": PREFIX.BUILDING_INFRA.alias_uri('contains'),
        "spaces": PREFIX.BUILDING_INFRA.alias_uri('inContactWith'),
        "building": PREFIX.BUILDING_INFRA.alias_uri('contains'),
        "orientation": PREFIX.BUILDING_INFRA.alias_uri('hasOrientation')
    }

    REFERENCES = {
        "building_id": PREFIX.IFC2x3.alias_uri('IfcBuilding'),
        "spaces": [PREFIX.IFC2x3.alias_uri('IfcSpatialElement')],
    }

    REFERENCES_ENUM = {
        'orientation': {
            'prefix': PREFIX.BUILDING_INFRA,
            'type': PREFIX.BUILDING_INFRA.alias_uri('Orientation'),
            'indiv': True}
    }

    DIMENSIONS = {
        'area': 'Area',
        'max_height': 'Height',
        'width': 'Width',
    }

    FILTERS_REF = {
        "space_id": "?URI {rel} {prefix}:{{id}}\n".format(
            rel=LINKS['spaces'], prefix=PREFIX.ROOT.alias)
    }

    CLASS_TO_FIELD_TO_RELATION = {
        Facade: FIELD_TO_RELATION,
        SurfaceInfo: DIMENSIONS,
    }

    SCHEMA = FacadeSchema

    def _str_select(self, field, optional=False):
        """Build select line

        :param str field: Field name
        :param bool optional: Whether the field is optional (defaults to False)
        """
        return self._build_select_line(
            field, self.FIELD_TO_RELATION[field], optional=optional)

    def _build_select_query(self, identifier=None, **filters):
        """A method to build the select query
        :return string: a string for the SPARQL query"""
        _select = ["""SELECT ?URI ?orientation"""] + \
            list(self.FIELD_TO_RELATION.keys()) +\
            list(self.FIELD_TO_REL_CPLX.keys())
        select = ' ?'.join(_select)
        query = """{sel} WHERE {{
                           ?cls rdfs:subClassOf* {clss}.
                           ?URI a ?cls.
                """.format(sel=select,
                           clss=PREFIX.IFC2x3.alias_uri('IfcWall'),)
        if identifier is not None:
            query += """?URI {} "{}".\n""".format(
                self.FIELD_TO_RELATION["id"],
                str(identifier))
        query += self._str_select("id")
        query += self._str_select("name")
        query += self._str_select("windows_wall_ratio", optional=True)
        query += self._str_select("interior")
        query += self._str_select("description", optional=True)
        query += self._build_select_line(
            'orientation', self.LINKS['orientation'], optional=True)
        query += self.FIELD_TO_REL_CPLX['building_id']
        # handle filter
        query += self._build_filters(**filters)
        query += "}"
        return query

    def _build_filters(self, **filters):
        '''Build the string for filtering'''
        filters, filter_str = super().str_filter_parent(**filters)
        filter_str += str_filter(
            {x: filters[x] for x in filters if x not in self.FILTERS_REF})
        return filter_str + str_filter_relation(filters, self.FILTERS_REF)

    def _pre_load_binding(self, binding):
        if 'orientation' in binding:
            binding['orientation'] = PREFIX.get_name(binding['orientation'])
        # Get quantities
        binding['surface_info'] = self._create_surface_info_binding(
            PREFIX.ROOT.alias_uri(binding['id']))
        # Get deilimited elements
        binding['spaces'] = list(self.get_related_individuals_id(
            PREFIX.ROOT.alias_uri(binding['id']),
            self.LINKS["spaces"],
            PREFIX.IFC2x3.alias_uri('IfcSpatialElement')))
        # Get windows
        binding['windows'] = list(self.get_related_individuals_id(
            PREFIX.ROOT.alias_uri(binding['id']),
            self.LINKS["windows"],
            PREFIX.IFC2x3.alias_uri('IfcWindow')))

    def _build_create_query(self, _id, element):
        _class = PREFIX.IFC2x3.alias_uri('IfcWall')
        # Build the query
        query = """{{
                {0} a {1};
                    {2} "{3}" ;
                """.format(PREFIX.ROOT.alias_uri(_id),
                           _class,
                           PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                           _id)
        query += self._str_insert(element, "windows_wall_ratio", optional=True)
        query += self._str_insert(element, "interior", optional=True)
        query += self._str_insert(element, "description", optional=True)
        query += str_insert(self.LINKS, element, 'orientation', optional=True,
                            prefix=PREFIX.BUILDING_INFRA)
        query += self._str_insert(element, "name", final=True)
        query += "}"
        return query

    def create(self, element):
        _id = super().create(element)
        my_uri = PREFIX.ROOT.alias_uri(_id)
        # Add relation with parent
        parent_uri = PREFIX.ROOT.alias_uri(element.building_id)
        self._create_relation_to(parent_uri, self.LINKS['building'], my_uri)
        # Add links with spatial elements in contact with
        for elt_id in element.spaces:
            self._create_relation_to(my_uri, self.LINKS['spaces'],
                                     PREFIX.ROOT.alias_uri(elt_id))
        # Create quantities
        self.create_quantities(element.surface_info.get_quantities(), my_uri)
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
        return self._build_remove(uri, self.FIELD_TO_RELATION.values())

    def update(self, identifier, new_element):
        """Update the element identified by its ID - replace it with the
        element new_element

        :param identifier identifier: a unique identifier for the element to
            be updated
        :param new_element Thing: the new elements that should replace the one
            identified by identifier
        """
        super().update(identifier, new_element)
        if new_element.surface_info:
            self.update_properties(
                identifier, new_element.surface_info.get_quantities())
