"""IFC data converter to model"""

from functools import reduce

from ifc_datareader import IfcObjectEntity

from ...models import (
    Site, GeographicInfo,
    Building,
    Floor,
    Zone,
    Space, SpaceOccupancy,
    Facade, Slab,
    Window,
    SpatialInfo, SurfaceInfo)
from ...tools.geo_location import convert_dms_to_dd, deduce_hemisphere_from_dms


class IfcConvertorError(Exception):
    """Conversion Error"""


class IfcConverter():
    """Convert an IFC entity to a model instance"""

    @staticmethod
    def _check(ifc_obj_entity, ifc_type_expected):
        if (not isinstance(ifc_obj_entity, IfcObjectEntity)
                and not ifc_obj_entity.ifc_type == ifc_type_expected):
            raise TypeError(
                'Invalid IfcObjectEntity instance: {}'.format(ifc_obj_entity))

    @staticmethod
    def _check_multiple(ifc_obj_entity, ifc_types_expected):
        for ifc_type in ifc_types_expected:
            IfcConverter._check(ifc_obj_entity, ifc_type)

    @staticmethod
    def _get_element(list_objects, type_name, names, exclude_names, default,
                     f_get_type):
        if not list_objects:
            return None
        _exclude_names = exclude_names or []
        filtered_objects = {
            obj.name: obj.value for obj in list_objects
            if f_get_type(obj) == type_name and obj.name not in _exclude_names}
        for name in names:
            if name in filtered_objects:
                return filtered_objects.get(name)
        if default and len(filtered_objects) > 0:
            return list(filtered_objects.values())[0]
        return None

    @staticmethod
    def _get_quantity(element, type_name, names, exclude_names=None,
                      default=False):
        """Get the quantity value associated to element, whose type must be
        type. Names are part of the names list and exclude_names are
        rejected"""
        return IfcConverter._get_element(
            element.quantities, type_name, names, exclude_names, default,
            lambda q: q.type_name)

    @staticmethod
    def _get_property(element, type_name, names, exclude_names=None,
                      default=False, pset_names=None):
        """Get the quantity value associated to element, whose type must be
        type. Names are part of the names list and exclude_names are
        rejected"""
        # COMPUTE THE PSETS SELECTED
        psets = element.property_sets if not pset_names else \
            [pset for pset in element.property_sets if pset.name in pset_names]
        properties = reduce(
            lambda x, y: x+y, map(lambda x: list(x.properties), psets), [])
        elt = IfcConverter._get_element(
            properties, type_name, names, exclude_names, False,
            lambda p: p.value_type_name)
        # No result - look in every associated PSETS
        if not elt and default:
            properties = reduce(
                lambda x, y: x+y,
                map(lambda x: list(x.properties), element.property_sets), [])\
                if not pset_names else properties
            elt = IfcConverter._get_element(
                properties, type_name, names, exclude_names, True,
                lambda p: p.value_type_name)
        return elt

    @classmethod
    def to_site(cls, ifc_site):
        """Convert IfcSite entity to Site model"""
        cls._check(ifc_site, 'IfcSite')

        hemisphere = 'Northern'
        if deduce_hemisphere_from_dms(ifc_site.info['RefLongitude']) == 'S':
            hemisphere = 'Southern'
        geo_info = GeographicInfo(
            latitude=convert_dms_to_dd(ifc_site.info['RefLatitude']),
            longitude=convert_dms_to_dd(ifc_site.info['RefLongitude']),
            altitude=ifc_site.info['RefElevation'],
            hemisphere=hemisphere
        )

        return Site(
            name=ifc_site.name, geographic_info=geo_info,
            description=ifc_site.description)

    @classmethod
    def to_building(cls, ifc_building, site_id):
        """Convert IfcBuilding entity to Building model"""
        cls._check(ifc_building, 'IfcBuilding')
        area = cls._get_quantity(
            ifc_building, 'IfcQuantityArea',
            ['GrossFloorArea', 'NetFloorArea', 'NominalArea'],
            default=True)

        return Building(
            name=ifc_building.name,
            description=ifc_building.description,
            # TODO: 'Building' types are not informed in IFC
            kind=None,
            area=area, site_id=site_id)

    @classmethod
    def to_floor(cls, ifc_building_storey, building_id, level=None):
        """Convert IfcBuildingStorey entity to Floor model"""
        cls._check(ifc_building_storey, 'IfcBuildingStorey')

        spatial_info = SpatialInfo(
            area=cls._get_quantity(
                ifc_building_storey, 'IfcQuantityArea',
                ['GrossFloorArea', 'NetFloorArea', 'NominalArea']),
            max_height=cls._get_quantity(
                ifc_building_storey, 'IfcQuantityLength', ['NominalHeight']),
            volume=cls._get_quantity(
                ifc_building_storey, 'IfcQuantityVolume',
                ['GrossVolume', 'NetVolume'], default=True)
        )

        return Floor(
            name=ifc_building_storey.name,
            # TODO: Kinds cannot be obtained
            kind=None,
            level=level, spatial_info=spatial_info,
            description=ifc_building_storey.description,
            building_id=building_id)

    @classmethod
    def to_space(cls, ifc_space, floor_id):
        """Convert IfcSpace entity to Space model"""
        cls._check(ifc_space, 'IfcSpace')

        spatial_info = SpatialInfo(
            area=cls._get_quantity(
                ifc_space, 'IfcQuantityArea',
                ['GrossFloorArea', 'NetFloorArea', 'NominalArea'],
                default=True),
            max_height=cls._get_quantity(
                ifc_space, 'IfcQuantityLength',
                ['NominalHeight, ClearHeight']),
            volume=cls._get_quantity(
                ifc_space, 'IfcQuantityVolume', ['GrossVolume', 'NetVolume'],
                default=True)
        )

        occupancy = SpaceOccupancy(
            nb_permanents=cls._get_property(
                ifc_space, 'IfcCountMeasure', ['OccupancyNumber'],
                pset_names=['Pset_SpaceOccupancyRequirements']),
            nb_max=cls._get_property(
                ifc_space, 'IfcCountMeasure', ['OccupancyNumberPeak'],
                pset_names=['Pset_SpaceOccupancyRequirements']),
        )

        return Space(
            name=ifc_space.info['LongName'] or ifc_space.name,
            description=ifc_space.description,
            kind=None,  # TODO: how to get this data?
            occupancy=occupancy,
            spatial_info=spatial_info,
            floor_id=floor_id)

    @staticmethod
    def _get_building(ifc_entity):
        if ifc_entity.type_name == 'IfcSpace':
            return ifc_entity.parent.parent
        if ifc_entity.type_name == 'IfcBuildingStorey':
            return ifc_entity.parent
        else:
            raise TypeError

    @classmethod
    def to_zone(cls, ifc_zone, map_id):
        """Convert IfcZone entity to Zone model"""
        cls._check(ifc_zone, 'IfcZone')

        rel_elements = ifc_zone.kids
        # get building id
        set_building_id =\
            {map_id(cls._get_building(elt)) for elt in rel_elements}
        if len(set_building_id) != 1:
            raise TypeError

        zone = Zone(
            name=ifc_zone.name, description=ifc_zone.description,
            building_id=set_building_id.pop(),
            spaces=[map_id(elt) for elt in rel_elements
                    if elt.type_name == 'IfcSpace'],
            zones=[map_id(elt) for elt in rel_elements
                   if elt.type_name == 'IfcZone']
        )

        return zone

    @classmethod
    def to_facade(cls, ifc_wall, map_id):

        """Converts IfcWall into H2G Facade"""
        cls._check_multiple(ifc_wall, ('IfcWall', 'IfcWallStandardCase'))

        # TODO: get a clearer understanding of the different areas informed in\
        # TODO: IFC - For now: get the first available area associated...
        area = cls._get_quantity(
            ifc_wall, 'IfcQuantityArea', names=[], default=True) or\
            cls._get_property(
                ifc_wall, 'IfcAreaMeasure', names=['Area'], default=True)
        height = cls._get_quantity(
            ifc_wall, 'IfcQuantityLength', names=['NominalHeight']) or\
            cls._get_property(ifc_wall, 'IfcLengthMeasure', ['Height'])
        width = cls._get_quantity(
            ifc_wall, 'IfcQuantityLength', ['NominalWidth']) or\
            cls._get_property(ifc_wall, 'IfcLengthMeasure', ['Width'])

        surface_info = SurfaceInfo(area=area, max_height=height, width=width)

        wall = Facade(
            name=ifc_wall.name, description=ifc_wall.description,
            building_id=map_id(cls._get_building(ifc_wall.parent)),
            surface_info=surface_info,
            spaces=[map_id(elt) for elt in ifc_wall.kids
                    if elt.type_name == 'IfcSpace'],
            interior=not cls._get_property(
                ifc_wall, 'IfcBoolean', ['IsExternal'],
                pset_names=['Pset_WallCommon'])
        )
        return wall

    @classmethod
    def to_slab(cls, ifc_slab, map_id):

        """Converts IfcWall into H2G Facade"""
        cls._check_multiple(ifc_slab, ('IfcSlab'))

        area = cls._get_quantity(
            ifc_slab, 'IfcQuantityArea', names=['GroosArea, NetArea'],
            default=True) or\
            cls._get_property(
                ifc_slab, 'IfcAreaMeasure', names=['Area'], default=True)
        width = cls._get_quantity(
            ifc_slab, 'IfcQuantityLength', ['NominalWidth']) or\
            cls._get_property(ifc_slab, 'IfcLengthMeasure', ['Width'])

        surface_info = SurfaceInfo(area=area, width=width)
        parent = ifc_slab.parent

        kind_map = {'FLOOR': 'FloorSlab', 'BASE': 'BaseSlab', 'ROOF': 'Roof'}

        slab = Slab(
            name=ifc_slab.name, description=ifc_slab.description,
            building_id=map_id(cls._get_building(parent)),
            surface_info=surface_info,
            floors=[map_id(parent)]
            if parent.type_name == 'IfcBuildingStorey' else [],
            kind=kind_map.get(ifc_slab.get_attribute('PredefinedType'), None)
        )
        return slab

    @classmethod
    def to_window(cls, ifc_window, map_id, reader):

        """Converts IfcWindow into H2G Window"""
        cls._check(ifc_window, 'IfcWindow')

        # get the opening in which the window is put
        rels_opening = ifc_window.get_relations('FillsVoids')
        ifc_opening =\
            reader.get_object(rels_opening[0].RelatingOpeningElement) \
            if rels_opening else None
        # TODO: add Slab and Roof in model: some of the windows may be\
        # TODO: integrated in such elements
        if not ifc_opening:
            raise IfcConvertorError()
        parent_id = map_id(ifc_opening.parent)
        if not parent_id or parent_id == 'None':
            raise IfcConvertorError()

        area = \
            cls._get_quantity(ifc_opening, 'IfcQuantityArea',
                              names=['NominalArea'], default=True) if\
            ifc_opening else cls._get_quantity(
                ifc_window, 'IfcQuantityArea', names=[], default=True)
        height = ifc_window.get_attribute('OverallHeight') or \
            cls._get_property(ifc_window, 'IfcLengthMeasure', ['Height']) or\
            (cls._get_property(ifc_opening, 'IfcLengthMeasure', ['Height'])
             if ifc_opening else None)
        width = ifc_window.get_attribute('OverallWidth') or \
            cls._get_property(ifc_window, 'IfcLengthMeasure', ['Width']) or\
            (cls._get_property(ifc_opening, 'IfcLengthMeasure', ['Width'])
             if ifc_opening else None)

        surface_info = SurfaceInfo(area=area, max_height=height, width=width)
        glazing_layers = cls._get_property(
            ifc_window, 'IfcCountMeasure', ['GlassLayers'],
            pset_names=['Pset_DoorWindowGlazingType'])
        glazing = 'SimpleGlazing' if glazing_layers == 1 else\
            'DoubleGlazing' if glazing_layers == 2 else\
            'TripleGlazing' if glazing_layers == 3 else None
        u_value = cls._get_property(
            ifc_window, 'IfcThermalTransmittanceMeasure',
            ['ThermalTransmittance'],
            pset_names=['Pset_DoorWindowGlazingType'])

        window = Window(
            name=ifc_window.name, description=ifc_window.description,
            facade_id=parent_id, surface_info=surface_info, glazing=glazing,
            u_value=u_value, covering=None)
        return window
