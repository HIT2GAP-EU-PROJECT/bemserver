"""Fixtures for database tests."""

import uuid
import pytest

from bemserver.database import (
    SiteDB, BuildingDB, FloorDB, SpaceDB, ZoneDB, FacadeDB, SlabDB, WindowDB,
    SensorDB, MeasureDB, ServiceDB, ModelDB)

from bemserver.models import (
    Site, GeographicInfo, Building, Floor, Space, SpaceOccupancy, Zone,
    SurfaceInfo, Facade, Slab, Window, Localization, Sensor, Measure,
    Service, Model, Parameter)


# -------------------------SITE--------------------------------

def _get_site_ids():
    return [
        uuid.UUID('0f32b7ee-083f-11e8-b911-0800278dbbf8'),
        uuid.UUID('194e6476-083f-11e8-b911-0800278dbbf8'),
    ]


@pytest.fixture()
def init_sites():
    geo_info = GeographicInfo(44.803652, -0.600954, altitude=20)
    sites = [
        Site('Site #{}'.format(idx+1), geo_info, id=site_id)
        for idx, site_id in enumerate(_get_site_ids())]
    return [SiteDB().create(site) for site in sites]


# -------------------------BUILDING--------------------------------

@pytest.fixture()
def get_building_ids():
    return [
        uuid.UUID('b61ce994-083f-11e8-b911-0800278dbbf8'),
        uuid.UUID('b653d2a6-083f-11e8-b911-0800278dbbf8'),
    ]


@pytest.fixture()
def get_created_building_ids():
    return created_building_ids


created_building_ids = []


@pytest.fixture()
def init_buildings():
    site_ids = init_sites()
    global created_building_ids
    buildings = [
        Building('Building #{}'.format(idx+1), 'BarRestaurant', site_ids[0],
                 id=building_id)
        for idx, building_id in enumerate(get_building_ids())]
    result = [BuildingDB().create(building) for building in buildings]
    created_building_ids = [id_ for id_ in result]
    return result


# -------------------------FLOOR--------------------------------

def _get_floor_ids():
    return [
        uuid.UUID('ea644b62-0843-11e8-b911-0800278dbbf8'),
        uuid.UUID('ea8ed9f4-0843-11e8-b911-0800278dbbf8'),
    ]


@pytest.fixture()
def init_floors():
    building_ids = init_buildings()
    floors = [
        Floor(
            'Floor #{}'.format(idx+1), 0, building_ids[0], 'Floor',
            id=floor_id)
        for idx, floor_id in enumerate(_get_floor_ids())]
    return [FloorDB().create(floor) for floor in floors]


# -------------------------SPACE--------------------------------

def _get_space_ids():
    return [
        uuid.UUID('23e48032-0a5b-11e8-b911-0800278dbbf8'),
        uuid.UUID('241a1cba-0a5b-11e8-b911-0800278dbbf8'),
    ]


@pytest.fixture()
def init_spaces():
    floor_ids = init_floors()
    space_occ = SpaceOccupancy(9, 20)
    spaces = [
        Space('Space #{}'.format(idx+1), floor_ids[0], 'OpenSpace',
              space_occ, id=space_id)
        for idx, space_id in enumerate(_get_space_ids())]
    return [SpaceDB().create(space) for space in spaces]


# -------------------------ZONE--------------------------------

def _get_zone_ids():
    return [
        uuid.UUID('2c5f53ca-0a62-11e8-b911-0800278dbbf8'),
        uuid.UUID('2c83f4fa-0a62-11e8-b911-0800278dbbf8'),
    ]


@pytest.fixture()
def init_zones():
    space_ids = init_spaces()
    building_ids = get_created_building_ids()
    zones = [
        Zone('Zone #{}'.format(idx+1), [], space_ids, building_ids[0],
             'A sample zone', id=zone_id)
        for idx, zone_id in enumerate(_get_zone_ids())]
    return [ZoneDB().create(zone) for zone in zones]

# -------------------------FACADE--------------------------------


def _get_facade_ids():
    return [
        uuid.UUID('fa28fdf7-02a8-4a0c-a97d-50727624181d'),
        uuid.UUID('80064876-45ac-4c16-8fad-e06cc83ea97f'),
    ]


@pytest.fixture()
def init_facades():
    space_ids = init_spaces()
    building_ids = get_created_building_ids()
    facades = [
        Facade('Facade #{}'.format(idx+1), space_ids,
               SurfaceInfo(25, 3.54, 0.012), building_ids[0], 0.23243,
               description='A sample facade', interior=True, id=facade_id)
        for idx, facade_id in enumerate(_get_facade_ids())]
    return [FacadeDB().create(facade) for facade in facades]

# -------------------------FACADE--------------------------------


def _get_slab_ids():
    return [
        uuid.UUID('998f2f4a-94ee-4c16-aec1-ec911460f19d'),
        uuid.UUID('e4f5f2d3-fe8f-4162-acd3-20ef38eb9322'),
    ]


@pytest.fixture()
def init_slabs():
    floors_ids = init_floors()
    building_ids = get_created_building_ids()
    slabs = [
        Slab('Slab #{}'.format(idx+1), [floors_ids[0], floors_ids[1]],
             SurfaceInfo(25, 3.54, 0.012), building_ids[0],
             description='A sample slab', kind='FloorSlab', id=slab_id)
        for idx, slab_id in enumerate(_get_slab_ids())]
    return [SlabDB().create(slab) for slab in slabs]

# -------------------------WINDOW--------------------------------


def _get_window_ids():
    return [
        uuid.UUID('c164f2a8-2a97-4db4-9727-bd04495eadf1'),
        uuid.UUID('f8e28f66-0a39-403b-8cba-712d8c878891'),
    ]


@pytest.fixture()
def init_windows():
    facades_ids = init_facades()
    windows = [
        Window('Window #{}'.format(idx+1), facades_ids[1],
               SurfaceInfo(25, 3.54, 0.012), description='A sample window',
               covering='Blind', glazing='SimpleGlazing', u_value=12.34)
        for idx, _ in enumerate(_get_facade_ids())]
    return [WindowDB().create(window) for window in windows]

# -------------------------SENSOR--------------------------------


def _get_sensor_ids():
    return [
        uuid.UUID('905736c9-2e1b-45a9-9c51-a263c5a24210'),
        uuid.UUID('30a43015-23ec-45ca-a6b6-5fee73f7d3cb'),
    ]


@pytest.fixture()
def init_sensors():
    space_ids = init_spaces()
    sensors = [
        Sensor('Sensor #{}'.format(idx+1),
               localization=Localization(space_id=space_ids[1]),
               description='A sample sensor')
        for idx, _ in enumerate(_get_sensor_ids())]
    return [SensorDB().create(sensor) for sensor in sensors]

# -------------------------MEASURE--------------------------------


def _get_measure_ids():
    return [
        uuid.UUID('cd2a4a7c-3f0b-4297-94f8-70c20cec3e66'),
        uuid.UUID('4f53c760-ec06-4bdb-9556-8263bb9d1959'),
    ]


@pytest.fixture()
def init_measures():
    sensor_ids = init_sensors()
    space_ids = init_spaces()
    measures = [
        Measure(str(sensor_ids[idx]), 'DegreeCelsius', 'Air', 'Temperature',
                description='A sample measure #{}'.format(idx+1),
                associated_locations=[space_ids[0]])
        for idx, _ in enumerate(_get_measure_ids())]
    return [MeasureDB().create(measure) for measure in measures]

# -------------------------SERVICES--------------------------------


def _get_service_urls():
    return [
        'http://hit2gap.eu/fdd', 'http://hit2gap.eu/forecasting'
    ]


@pytest.fixture()
def _get_service_ids():
    return [
        uuid.UUID('15770284-2ab5-4a0c-8dd6-fcc29bc9df8d'),
        uuid.UUID('590870fa-a2f5-4374-80d5-fe77ccbc2eb5'),
    ]


@pytest.fixture()
def init_services():
    services = [
        Service('ServiceFDD#{}'.format(idx+1),
                description='A fake fault and detection diagnosis service',
                url=_get_service_urls()[idx],
                id=id_)
        for idx, id_ in enumerate(_get_service_ids())]
    return [ServiceDB().create(service) for service in services]

# -------------------------MODELS--------------------------------


def _get_model_ids():
    return [
        uuid.UUID('cabe3962-44a6-48ad-98f9-1093d7227887'),
        uuid.UUID('4a8676f8-4cbe-4ce3-bad4-8547652e7b96'),
    ]


@pytest.fixture()
def init_models():
    service = init_services()[0]
    params = [[Parameter('ar', 1), Parameter('I', 2), Parameter('MA', 0)],
              [Parameter('gamma', 0.543)]]
    models = [
        Model('ARIMA#1', service, description='A sample model #1',
              parameters=params[0]),
        Model('SVR #1', service, description='A sample model #2',
              parameters=params[1])]
    return [ModelDB().create(model) for model in models]
