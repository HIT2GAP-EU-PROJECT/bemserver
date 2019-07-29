"""Serialize/deserialize elements into the data storage solution"""

import abc

from .ontology.manager import SPARQLOP, PREFIX, ontology_manager_factory
from ..models.tree import Node


class AbsDBEnum(abc.ABC):
    """An interface for access to enumeration types in the data model."""

    #########
    # Building information

    @abc.abstractmethod
    def get_building_types(self):
        """Get values for building types."""

    @abc.abstractmethod
    def get_floor_types(self):
        """Get values for floor types"""

    @abc.abstractmethod
    def get_space_types(self):
        """Get values for space types."""

    @abc.abstractmethod
    def get_slab_types(self):
        """Get values for slab types."""

    @abc.abstractmethod
    def get_window_covering_types(self):
        """Get values for window covering types."""

    #########
    # Geographical information

    @abc.abstractmethod
    def get_hemisphere_types(self):
        """Get values for hemisphere types."""

    @abc.abstractmethod
    def get_climate_types(self):
        """Get values for climate types."""

    @abc.abstractmethod
    def get_orientation_types(self):
        """Get values for orientation types."""

    @abc.abstractmethod
    def get_energy_sources(self):
        """Get values for enery sources."""

    @abc.abstractmethod
    def get_renewable_energy_sources(self):
        """Get values for renewable enery sources."""

    @abc.abstractmethod
    def get_non_renewable_energy_sources(self):
        """Get values for non-renewable enery sources."""

    #########
    # Energy information

    # renewable
    # non-renewable
    # other

    #########
    # Systems information

    @abc.abstractmethod
    def get_system_types(self):
        """Get values for system types."""

    #########
    # Measure information

    @abc.abstractmethod
    def get_observation_types(self):
        """Get values for observation types."""

    @abc.abstractmethod
    def get_medium_types(self):
        """Get values for medium types."""

    @abc.abstractmethod
    def get_temperature_units(self):
        """Get units for temperature."""

    @abc.abstractmethod
    def get_units(self):
        """Get all units."""

    @abc.abstractmethod
    def get_humidity_units(self):
        """Get units for humidity."""

    @abc.abstractmethod
    def get_pressure_units(self):
        """Get units for pressure."""

    @abc.abstractmethod
    def get_flow_units(self):
        """Get units for flow."""

    @abc.abstractmethod
    def get_power_units(self):
        """Get units for power."""

    @abc.abstractmethod
    def get_electric_current_units(self):
        """Get units for electric current."""

    @abc.abstractmethod
    def get_electric_charge_units(self):
        """Get units for electric charge."""

    @abc.abstractmethod
    def get_radiance_units(self):
        """Get units for radiance."""

    @abc.abstractmethod
    def get_length_units(self):
        """Get units for length."""

    @abc.abstractmethod
    def get_distance_units(self):
        """Get units for distance."""

    @abc.abstractmethod
    def get_volume_units(self):
        """Get units for volume."""

    @abc.abstractmethod
    def get_location_types(self):
        """Get values for location types."""

    @abc.abstractmethod
    def get_occupant_states(self):
        """Get values for occupant states."""

    #########
    # Occupancy information

    @abc.abstractmethod
    def get_gender_types(self):
        """Get values for gender types."""

    @abc.abstractmethod
    def get_age_categories(self):
        """Get values for age categories."""


class DBEnumHandler(AbsDBEnum):
    """Class to handle enums and types in the data model."""

    SUBCLASS_INSTANCE = """
        SELECT ?class ?parent ?indiv ?label
        WHERE {{
            ?class rdfs:subClassOf* {}.
            {{?class rdfs:subClassOf ?parent. ?class rdfs:label ?label}} UNION
            {{?indiv rdf:type ?class}}.
        }}"""

    SUBCLASS = """
        SELECT ?label ?class ?parent
        WHERE {{
            ?class rdfs:subClassOf* {}.
            {{?class rdfs:subClassOf ?parent. ?class rdfs:label ?label}}.
        }}"""

    def __init__(self):
        self.onto_mgr = ontology_manager_factory.get_ontology_manager()

    def _get_enum(self, element, prefix, instance=True):
        """Execute queries to the triple store and build hierarchical
        enumerations with the result.

        :return Node: Tree node of enum values.
        """
        _query = self.SUBCLASS_INSTANCE if instance else self.SUBCLASS
        _query = _query.format(prefix.alias_uri(element))
        res = self.onto_mgr.perform(SPARQLOP.SELECT, _query)
        return self._build_tree('{}{}'.format(prefix.url, element), res)

    def _build_tree(self, uri, query_result):
        """Build enums based on JSON entries where hierarchies are specified.

        :param str uri: the URI of the entity which is the common parent
        :param QueryResult query_result: a `QueryResult` instance
        :result Node: Tree node of enum values.
        """
        name = PREFIX.get_name(uri)
        root = Node(name)
        for elt in query_result.values:
            if elt.get('parent') == uri:
                # elt is a class!!!
                child = self._build_tree(elt['class'], query_result)
                root.add_child(child)
            elif elt['class'] == uri and 'indiv' in elt:
                # element is a literal
                name = elt.get('label', PREFIX.get_name(elt['indiv']))
                root.add_child(Node(name))
        return root

    def get_building_types(self):
        """Return building types (from IFC2x3 ontology)."""
        result = self._get_enum('IfcBuilding', PREFIX.IFC2x3, instance=False)
        result.label = 'BuildingType'
        return result

    def get_floor_types(self):
        """Return floor types (from IFC2x3 ontology)."""
        result = self._get_enum(
            'Floor', PREFIX.BUILDING_INFRA, instance=False)
        result.label = 'Floor'
        return result

    def get_slab_types(self):
        """Return floor types (from IFC2x3 ontology)."""
        result = self._get_enum(
            'IfcSlab', PREFIX.IFC2x3, instance=False)
        result.label = 'Slab'
        return result

    def get_space_types(self):
        """Return space types (from IFC2x3 ontology)."""
        result = self._get_enum('IfcSpace', PREFIX.IFC2x3, instance=False)
        result.label = 'Space'
        return result

    def get_window_covering_types(self):
        """Return window covering types (from building ontology)."""
        result = self._get_enum('WindowCoveringType', PREFIX.BUILDING_INFRA)
        result.label = 'WindowCovering'
        return result

    def get_hemisphere_types(self):
        """Return hemisphere types (from sensor ontology)."""
        return self._get_enum('Hemisphere', PREFIX.BUILDING_INFRA)

    def get_climate_types(self):
        """Return climate types (from property ontology)."""
        return self._get_enum('Climate', PREFIX.BUILDING_INFRA)

    def get_orientation_types(self):
        """Return orientation types (from building ontology)."""
        return self._get_enum('Orientation', PREFIX.BUILDING_INFRA)

    def get_system_types(self):
        pass

    def get_units(self):
        unit_typenames = [
            'temperature', 'humidity', 'pressure', 'length', 'flow',
            'distance', 'volume', 'radiance', 'power', 'electric_current',
            'electric_charge']

        units = Node('Units')
        for unit_typename in unit_typenames:
            unit_funcname = 'get_{}_units'.format(unit_typename)
            units.add_child(getattr(self, unit_funcname)())
        return units

    def get_temperature_units(self):
        """Return temperature units (from QUDT ontology)."""
        return self._get_enum('TemperatureUnit', PREFIX.QUDT)

    def get_humidity_units(self):
        """Return humidity units (from QUDT ontology)."""
        return self._get_enum('HumidityUnit', PREFIX.QUDT)

    def get_pressure_units(self):
        """Return pressure units (from QUDT ontology)."""
        result = self._get_enum('PressureOrStressUnit', PREFIX.QUDT)
        result.label = 'PressureUnit'
        return result

    def get_length_units(self):
        """Get length units (from QUDT ontology)."""
        return self._get_enum('LengthUnit', PREFIX.QUDT)

    def get_flow_units(self):
        result = self._get_enum('VolumePerTimeUnit', PREFIX.QUDT)
        result.label = 'FlowUnit'
        return result

    def get_distance_units(self):
        return self._get_enum('AreaUnit', PREFIX.QUDT)

    def get_volume_units(self):
        return self._get_enum('VolumeUnit', PREFIX.QUDT)

    def get_radiance_units(self):
        return self._get_enum('RadianceUnit', PREFIX.QUDT)

    def get_power_units(self):
        """Return power units (from QUDT ontology)."""
        return self._get_enum('PowerUnit', PREFIX.QUDT)

    def get_electric_current_units(self):
        return self._get_enum('ElectricCurrentUnit', PREFIX.QUDT)

    def get_electric_charge_units(self):
        return self._get_enum('ElectricChargeUnit', PREFIX.QUDT)

    def get_location_types(self):
        pass

    def get_occupant_states(self):
        """Return occupant states (from property ontology)"""
        result = self._get_enum('OccupantStateProperties', PREFIX.PROPERTY)
        result.label = 'OccupantState'
        return result

    def get_gender_types(self):
        """Return gender types (from BEM ontology)."""
        return self._get_enum('Gender', PREFIX.OCCUPANT)

    # TODO in the module for OccupantDB
    def get_age_categories(self):
        pass

    def get_energy_sources(self):
        """Select all energy sources"""
        result = self._get_enum('DERBranch', PREFIX.ONTO_MG)
        result.label = 'EnergySource'
        return result

    def get_renewable_energy_sources(self):
        """Select all renewable energy sources"""
        result = self._get_enum('RenewableDERBranch', PREFIX.ONTO_MG)
        result.label = 'RenewableEnergySource'
        return result

    def get_non_renewable_energy_sources(self):
        """Select all non-renewable energy sources"""
        result = self._get_enum('NonRenewableDERBranch', PREFIX.ONTO_MG)
        result.label = 'NonRenewableEnergySource'
        return result

    def get_observation_types(self):
        """Get values for observation types."""
        result = self._get_enum('PhysicalProperty', PREFIX.PROPERTY)
        res_presence = self._get_enum('OccupantProperty', PREFIX.PROPERTY)
        result.add_child(res_presence)
        result.label = 'ObservationType'
        return result

    def get_medium_types(self):
        """Get values for medium types."""
        result = self._get_enum('PhysicalMedium', PREFIX.BUILDING_INFRA)
        result.label = 'MediumType'
        return result
