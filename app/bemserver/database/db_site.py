"""Serialize/deserialize elements into the data storage solution"""

from ..models.site import Site
from ..models.geography import GeographicInfo
from .ontology.generic import ThingDB
from .ontology.manager import PREFIX
from .schemas import SiteSchema
from .utils import str_insert, str_filter, str_filter_relation


class SiteDB(ThingDB):
    """A class to handle sites in the data storage solution"""

    FIELD_TO_RELATION = {
        'id': PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
        'name': PREFIX.IFC2x3.alias_uri('name_IfcRoot'),
        'description': PREFIX.IFC2x3.alias_uri('description_IfcRoot'),
    }

    GEO_FIELD_TO_RELATION = {
        'latitude': PREFIX.IFC2x3.alias_uri('refLatitude_IfcSite'),
        'longitude': PREFIX.IFC2x3.alias_uri('refLongitude_IfcSite'),
        'altitude': PREFIX.IFC2x3.alias_uri('refElevation_IfcSite'),
        'hemisphere': PREFIX.BUILDING_INFRA.alias_uri('locatedInHemisphere'),
        'climate': PREFIX.PROPERTY.alias_uri('locatedInClimate'),
    }

    CLASS_TO_FIELD_TO_RELATION = {
        Site: FIELD_TO_RELATION,
        GeographicInfo: GEO_FIELD_TO_RELATION,
    }

    # ... references from pre-existing individuals
    REFERENCES_ENUM = {
        'hemisphere': {
            'prefix': PREFIX.BUILDING_INFRA,
            'type': PREFIX.BUILDING_INFRA.alias_uri('Hemisphere'),
            'indiv': True},
    }

    FILTER_REF = {
        'climate':
            '''?cls {rel} ?kind_cls. ?kind_cls {rel_name} "{{id}}"\n'''.format(
                rel=PREFIX.RDFS.alias_uri('subClassOf*'),
                rel_name=PREFIX.RDFS.alias_uri('label')
            ),
    }

    SCHEMA = SiteSchema

    def _str_select(self, obj_class, field, optional=False):
        """Build select line

        :param type obj_class: Thing class
        :param str field: Field name
        :param bool optional: Whether the field is optional (defaults to False)
        """
        return self._build_select_line(
            field,
            self.CLASS_TO_FIELD_TO_RELATION[obj_class][field],
            optional=optional)

    def _build_select_query(self, identifier=None, **filters):
        """Build the select query

        :return string: a string for the SPARQL query
        """
        query = """SELECT ?id ?name ?description ?altitude ?latitude ?longitude
                          ?climate ?hemisphere
                   WHERE {{
                           ?URI a {uri} .
                """.format(uri=PREFIX.IFC2x3.alias_uri('IfcSite'))
        if identifier is not None:
            query += """?URI {} "{}".\n""".format(
                self.FIELD_TO_RELATION["id"], str(identifier))
        query += self._str_select(Site, "id")
        query += self._str_select(Site, "name")
        query += self._str_select(Site, "description", optional=True)
        query += self._str_select(GeographicInfo, "altitude", optional=True)
        query += self._str_select(GeographicInfo, "latitude")
        query += self._str_select(GeographicInfo, "longitude")
        query += self._str_select(GeographicInfo, "climate", optional=True)
        query += self._str_select(GeographicInfo, "hemisphere", optional=True)
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
        geo_info_keys = (
            'latitude', 'longitude', 'altitude', 'hemisphere', 'climate')
        binding['geographic_info'] = {
            key: binding.pop(key) for key in geo_info_keys if key in binding}

    def _build_create_query(self, _id, site):
        """Create sites into the data model

        :param site: A Site object to be created
        """
        # Build the query
        query = """{{
                {0} a {1};
                    {2} "{3}" ;
                """.format(PREFIX.ROOT.alias_uri(_id),
                           PREFIX.IFC2x3.alias_uri('IfcSite'),
                           PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                           _id)
        query += self._str_insert(site, "name")
        query += self._str_insert(site, "description", optional=True)
        query += self._str_insert(site.geographic_info, "latitude")
        query += self._str_insert(site.geographic_info, "longitude")
        query += self._str_insert(
            site.geographic_info, "altitude", optional=True)
        query += self._str_insert(
            site.geographic_info, "climate", optional=True)
        query += self._str_insert(
            site.geographic_info, "hemisphere", optional=True)
        query += "}"
        return query

    def _str_insert(self, obj, attr, optional=False):
        """Build up the line corresponding to an object attribute, into
        a SPARQL insert method, in the form "relation value". Value is
        extracted from obj.attr, the relation is extracted from a dictionary.

        :param subj String: the "subject" of the triple to be created
        :param obj Object: an object
        :param attr String: the name of the attribute
        :param optional boolean: True if the element to be inserted is optional
        :param return: a String to be inserted into the INSERT query, of the
            form rel value
        """
        return str_insert(
            self.CLASS_TO_FIELD_TO_RELATION[obj.__class__],
            obj, attr, optional=optional)

    def _get_delete_for_update(self, uri):
        """Build the delete query

        :param uri string: the uri of the object to be removed.
        :return string, string: a sparql delete clause, and where clause
        """
        rels = list(self.FIELD_TO_RELATION.values())
        rels.extend(list(self.GEO_FIELD_TO_RELATION.values()))
        return self._build_remove(uri, rels)
