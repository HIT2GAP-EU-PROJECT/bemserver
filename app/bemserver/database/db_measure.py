"""Serialize/deserialize Space into the data storage"""

from .ontology.generic import ThingDB
from .ontology.manager import PREFIX
from .schemas import MeasureSchema
from .utils import str_insert, str_filter


class MeasureDB(ThingDB):
    """A class to handle buildings in the data storage solution"""

    # Dictionary for direct relations - values
    FIELD_TO_RELATION = {
        'id': PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
        'description': PREFIX.IFC2x3.alias_uri('description_IfcRoot'),
        'method': PREFIX.BUILDING_INFRA.alias_uri('hasObservationMethod'),
        'external_id': PREFIX.BUILDING_INFRA.alias_uri('externalID'),
        'on_index': PREFIX.BUILDING_INFRA.alias_uri('isIndex'),
        'set_point': PREFIX.BUILDING_INFRA.alias_uri('isSetPoint'),
        'outdoor': PREFIX.BUILDING_INFRA.alias_uri('isOutdoor'),
        'ambient': PREFIX.BUILDING_INFRA.alias_uri('isAmbient'),
    }
    # Values for MeasureValueProperties
    FIELD_VALUE_PTIES = {
        'frequency': PREFIX.BUILDING_INFRA.alias_uri('frequency'),
        'vmax': PREFIX.BUILDING_INFRA.alias_uri('maxValue'),
        'vmin': PREFIX.BUILDING_INFRA.alias_uri('minValue'),
    }
    # Values for MeasureMaterialProperties
    FIELD_MATERIAL_PTIES = {
        'latency': PREFIX.BUILDING_INFRA.alias_uri('latency'),
        'accuracy': PREFIX.BUILDING_INFRA.alias_uri('accuracy'),
        'precision': PREFIX.BUILDING_INFRA.alias_uri('precision'),
        'sensitivity': PREFIX.BUILDING_INFRA.alias_uri('sensitivity'),
    }

    # Dictionaries for attributes that require access to additional
    # concepts/instances
    LINKS = {
        # 'sensor': PREFIX.BUILDING_INFRA.alias_uri('isContainedIn'),
        'sensor': PREFIX.SOSA.alias_uri('madeBySensor'),
    }
    # ... dictionary for attributes that must refer to individuals initially in
    # the data model
    LINKS_ENUMERATE = {
        'observation_type': PREFIX.SSN.alias_uri('observedProperty'),
        'medium': PREFIX.SOSA.alias_uri('hasFeatureOfInterest'),
        'unit': PREFIX.PROPERTY.alias_uri('hasUnit'),
    }
    # ... references that are optional for measures
    OPT_LINKS = {
        # 'property': PREFIX.PROPERTY.alias_uri('hasMeasurementProperty'),
        'associated_locations': PREFIX.SOSA.alias_uri('hasFeatureOfInterest'),
    }

    # Check references exist
    REFERENCES = {
        'sensor': PREFIX.SOSA.alias_uri('Sensor'),
        'associated_locations': [PREFIX.IFC2x3.alias_uri('IfcSpatialElement')],
    }
    # ... references from pre-existing individuals
    REFERENCES_ENUM = {
        'medium': {
            'prefix': PREFIX.BUILDING_INFRA,
            'type': PREFIX.BUILDING_INFRA.alias_uri('PhysicalMedium'),
            'indiv': False},
        'observation_type': {
            'prefix': PREFIX.PROPERTY,
            'type': PREFIX.PROPERTY.alias_uri('PhenomenonProperty'),
            'indiv': False},
        'unit': {
            'prefix': [PREFIX.UNIT, PREFIX.PROPERTY],
            'type': PREFIX.QUDT.alias_uri('Unit'),
            'indiv': True},
    }

    FIELD_TO_REL_CPLX = {
        'sensor_id': """?URI {rel} ?sensor. ?sensor {rel_id} ?sensor_id.
            FILTER EXISTS {{?sensor_cls rdfs:subClassOf* {type}.
            ?sensor a ?sensor_cls}}.\n""".format(
                type=REFERENCES['sensor'],
                rel_id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
                rel=LINKS['sensor']),
        'medium': """OPTIONAL {{?URI {rel} ?medium_cls.
            ?medium_cls {rel_id} ?medium.
            FILTER EXISTS {{?medium_cls rdfs:subClassOf* {type}.}}}}.
            \n""".format(
                type=REFERENCES_ENUM['medium']['type'],
                rel_id=PREFIX.RDFS.alias_uri('label'),
                rel=LINKS_ENUMERATE['medium']),
        'observation_type': """OPTIONAL {{?URI {rel} ?obs_type.
            ?obs_type {rel_id} ?observation_type.
            FILTER EXISTS {{?obs_type_cls rdfs:subClassOf* {type}}}}}.
            \n""".format(
                type=REFERENCES_ENUM['observation_type']['type'],
                rel_id=PREFIX.RDFS.alias_uri('label'),
                rel=LINKS_ENUMERATE['observation_type']),
        'unit': """?URI {rel} ?unit.
            FILTER EXISTS {{?unit_cls rdfs:subClassOf* {type}.
            ?unit a ?unit_cls}}.\n""".format(
                type=REFERENCES_ENUM['unit']['type'],
                rel=LINKS_ENUMERATE['unit']),
    }

    # FIELD_TO_REL_CPLX_MULTIPLE = {
    #     'associated_locations': """?URI {rel} ?location.
    #         ?location {rel_id} ?associated_location.
    #         FILTER EXISTS {{?location_cls rdfs:subClassOf* {type}.
    #         ?location a ?location_cls}}.\n""".format(
    #             type=REFERENCES['associated_locations'],
    #             rel_id=PREFIX.IFC2x3.alias_uri('globalID_IfcRoot'),
    #             rel=OPT_LINKS['associated_locations']),
    # }

    # FILTERS_OPT = {
    #     'system_type': """?URI {rel} ?sys.\n?sys a sys_class.\n
    #         ?sys_class rdfs:subClassOf* {prefix}:{{val}}.\n""".format(
    #             rel=LINKS['system'], prefix=PREFIX.IFC2x3.alias),
    #     'measures' : ''
    # }

    SCHEMA = MeasureSchema

    def _str_select(self, field, optional=False, dict_=None):
        """Build select line

        :param str field: Field name
        :param bool optional: Whether the field is optional (defaults to False)
        """
        dico = dict_ or (self.FIELD_TO_RELATION
                         if field in self.FIELD_TO_RELATION
                         else (self.FIELD_VALUE_PTIES
                               if field in self.FIELD_VALUE_PTIES else
                               self.FIELD_MATERIAL_PTIES))
        return self._build_select_line(field, dico[field], optional=optional)

    def _build_filter(self, **filters):
        '''Build a string to add filtering parameters to a SPARQL query
        :param filters dict: a dictionary of parameter names, values
        :return a string to be inserted in the query'''
        filters, filter_str = super().str_filter_parent(**filters)
        for _dict in [self.FIELD_TO_RELATION, self.FIELD_VALUE_PTIES,
                      self.FIELD_MATERIAL_PTIES, self.REFERENCES_ENUM]:
            filters_by_value = {
                k: filters[k] for k in _dict if k in filters}
            filter_str += str_filter(filters_by_value)
        # add filter on location
        if 'location_id' in filters:
            filter_str += '?URI {} {}'.format(
                self.OPT_LINKS['associated_locations'],
                PREFIX.ROOT.alias_uri(filters.pop('location_id')))
        return filter_str

    def _build_select_query(self, identifier=None, **filters):
        """A method to build the select query
        :return string: a string for the SPARQL query"""
        _select = [
            """SELECT ?URI"""] +\
            list(self.FIELD_TO_RELATION.keys()) +\
            list(self.FIELD_VALUE_PTIES.keys()) +\
            list(self.FIELD_MATERIAL_PTIES.keys()) +\
            list(self.FIELD_TO_REL_CPLX)
        select = ' ?'.join(_select)
        query = """{sel} WHERE {{
                           ?cls rdfs:subClassOf* {clss}.
                           ?URI a ?cls.
                """.format(sel=select,
                           clss=PREFIX.SOSA.alias_uri('Observation'),)
        if identifier is not None:
            query += """?URI {} "{}".\n""".format(
                self.FIELD_TO_RELATION["id"], str(identifier))
        if 'external_id' in filters:
            query += """?URI {} "{}".\n""".format(
                self.FIELD_TO_RELATION["external_id"],
                filters.pop('external_id'))
        query += self._str_select("id")
        query += self._str_select("description", optional=True)
        query += self._str_select("method")
        query += self._str_select("on_index")
        query += self._str_select("outdoor")
        query += self._str_select("set_point", optional=True)
        query += self._str_select("ambient", optional=True)
        query += self._str_select("external_id", optional=True)
        # add properties
        for attr_ in set(
                self.FIELD_VALUE_PTIES).union(set(self.FIELD_MATERIAL_PTIES)):
            query += self._str_select(attr_, optional=True)
        # get references
        for attr_ in self.FIELD_TO_REL_CPLX:
            query += self.FIELD_TO_REL_CPLX[attr_]
        # add filters
        query += self._build_filter(**filters)
        query += "}"
        return query

    def _get_locations(self, uri):
        """Performs the query to get the related locations"""
        location_types = {
            'site': 'IfcSite', 'building': 'IfcBuilding',
            'floor': 'IfcBuildingStorey', 'space': 'IfcSpace'}
        binding_locations = []
        for type_name in location_types:
            ids = self.get_related_individuals_id(
                uri, self.OPT_LINKS['associated_locations'],
                parent_cls=PREFIX.IFC2x3.alias_uri(location_types[type_name]))
            binding_locations.extend(list(map(
                lambda x: {'type': type_name, 'id': x}, ids
            )))
        return binding_locations

    def _pre_load_binding(self, binding):
        # get locations references
        binding['associated_locations'] = self._get_locations(
            PREFIX.ROOT.alias_uri(binding['id']))
        # uri = PREFIX.ROOT.alias_uri(binding['id_'])
        binding['unit'] = PREFIX.get_name(binding['unit'])
        value_pties = {
            k: binding.pop(k)
            for k in self.FIELD_VALUE_PTIES if k in binding}
        if value_pties:
            binding['value_properties'] = value_pties
        material_pties = {
            k: binding.pop(k)
            for k in self.FIELD_MATERIAL_PTIES if k in binding}
        if material_pties:
            binding['material_properties'] = material_pties

##############################################
#                   CREATION
#############################################

    def _build_create_query(self, _id, element):
        _class = PREFIX.SOSA.alias_uri('Observation')
        # Build the query
        query = """{{
                {0} a {1};
                    {2} "{3}" ;
                """.format(PREFIX.ROOT.alias_uri(_id),
                           _class,
                           self.FIELD_TO_RELATION['id'],
                           _id)
        query += self._str_insert(element, "description", optional=True)
        query += self._str_insert(element, "external_id", optional=True)
        query += self._str_insert(element, "method", optional=True)
        query += self._str_insert(element, "outdoor", optional=True)
        query += self._str_insert(element, "set_point", optional=True)
        query += self._str_insert(element, "ambient", optional=True)
        query += self._str_insert(element, "on_index", optional=True)
        # add additional properties
        if element.value_properties:
            for attr in self.FIELD_VALUE_PTIES:
                query += self._str_insert(
                    element.value_properties, attr, optional=True)
        if element.material_properties:
            for attr in self.FIELD_MATERIAL_PTIES:
                query += self._str_insert(
                    element.material_properties, attr, optional=True)
        # add references
        query += "{rel} {pref}:{id};".format(
            rel=self.LINKS['sensor'], pref=PREFIX.ROOT.alias,
            id=element.sensor_id)
        # Units - check which prefix first
        for prefix in self.REFERENCES_ENUM['unit']['prefix']:
            if self._check_exists(
                    element.unit, self.REFERENCES_ENUM['unit']['type'],
                    prefix, True):
                query += "{rel} {pref}:{id};".format(
                    rel=self.LINKS_ENUMERATE['unit'], pref=prefix.alias,
                    id=element.unit)
                break
        query += "{rel} {pref}:{id};".format(
            rel=self.LINKS_ENUMERATE['medium'],
            pref=PREFIX.BUILDING_INFRA.alias,
            id=element.medium)
        query += "{rel} {pref}:{id};".format(
            rel=self.LINKS_ENUMERATE['observation_type'],
            pref=PREFIX.PROPERTY.alias, id=element.observation_type)
        for location in element.associated_locations:
            query += "{rel} {pref}:{id};".format(
                rel=self.OPT_LINKS['associated_locations'],
                pref=PREFIX.ROOT.alias, id=location)
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
        dict_ = self.FIELD_TO_RELATION if attr in self.FIELD_TO_RELATION \
            else (self.FIELD_VALUE_PTIES if attr in self.FIELD_VALUE_PTIES
                  else self.FIELD_MATERIAL_PTIES)
        return str_insert(dict_, obj, attr, optional=optional, final=final)

    def _get_delete_for_update(self, uri):
        """Build the delete query. This method is specific to every object.

        :param uri string: the URI of the object to be removed.
        :return string, string: a SPARQL DELETE clause, and WHERE clause
        """
        # to_remove = list(self.FIELD_TO_RELATION.values())
        # to_remove.extend([
        #     self.OPT_LINKS.values(), self.FIELD_VALUE_PTIES.values(),
        #
        #     self.LINKS['system']])
        return self._build_remove(uri)  # , to_remove)

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
    #     #self._create_localization_relation(my_uri, new_element.localization)
    #     # Add links with system
    #     if new_element.system:
    #         self._create_relation_to(
    #             my_uri, self.LINKS['system'],
    #             PREFIX.ROOT.alias_uri(new_element.system))
