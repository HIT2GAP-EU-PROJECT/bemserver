"""Fixtures for api views tests"""

import os
from pathlib import Path
import datetime as dt
import time
from random import randint
import pytest

from bemserver.api.default_api_settings import TestingConfig
from bemserver.api import create_app
from bemserver.api.extensions.database import db_accessor
from bemserver.models.geography import GeographicInfo
from bemserver.models import (
    Site, Building, Floor, Space, Zone, Facade, Slab, Window)
from bemserver.models.space import SpaceOccupancy
from bemserver.models.spatial import (
    SpatialInfo, SurfaceInfo)  # , OrientedSpatialInfo)
from bemserver.models import (
    IFCFile, Occupant, AgeCategory,
    OccupantWorkspace, Comfort, ComfortPerception,
    Sensor, Measure, Localization)
from bemserver.models.modules import (
    Service, Model, Parameter,
    OutputEvent, OutputTimeSeries, ValuesDescription)

from bemserver.tools.account_generator import (
    generate_login_id, generate_pwd)

from bemserver.database.filestorage import FileStorageMgr
from bemserver.database.relational import db
from bemserver.database.security.security_manager import (
    SecurityManager, UserAccount)

from tests.api.utils import JSONResponse, build_file_obj
from tests.database.filestorage.conftest import (
    ifc_file_data, ifc_file_data_stream, ifc_zip_file_data,
    ifc_multi_zip_file_data)


class TestingConfigAuthCertificateEnabled(TestingConfig):
    """App config to test with certificate authentication"""
    AUTHENTICATION_ENABLED = True
    AUTH_CERTIFICATE_ENABLED = True


@pytest.fixture
def drop_db(request):
    """Drop database"""
    db_accessor.reset_db()


@pytest.fixture(params=[TestingConfig])
def init_app(request, drop_db, tmpdir, init_onto_mgr_fact):
    """Initialize application

    To test several configurations in a test function,
    override the params list using @pytest.mark.parametrize.

    :Example:
        @pytest.mark.parametrize(
            'init_app', [TestingConfigAuthHttpBasic], indirect=True)
    """
    config_class = request.param

    # Log temp dir
    log_dir = os.path.join(str(tmpdir), 'log')
    os.mkdir(log_dir)
    config_class.LOGGER_DIR = log_dir

    # Timeseries storage temp dir
    ts_dir = os.path.join(str(tmpdir), 'timeseries')
    os.mkdir(ts_dir)
    config_class.TIMESERIES_BACKEND_STORAGE_DIR = ts_dir

    # File storage temp dir
    fs_dir = os.path.join(str(tmpdir), 'file_repo')
    os.mkdir(fs_dir)
    config_class.FILE_STORAGE_DIR = fs_dir

    # Security manager user accounts storage temp dir
    security_dir = os.path.join(str(tmpdir), 'security')
    os.mkdir(security_dir)
    config_class.SECURITY_STORAGE_DIR = security_dir

    # Create app with test config
    request.cls.app = create_app(config_class=config_class)

    # SQL database: create tables
    db.create_all(app=request.cls.app)

    # Use custom JSONResponse
    request.cls.app.response_class = JSONResponse

    # Launch app test client
    request.cls.client = request.cls.app.test_client()

    # Pass config to test function
    request.cls.config = config_class


def _create_sites():
    sites_data = [
        {'name': 'site_A', },
        {'name': 'site_B', },
        {'name': 'site_C', },
        {'name': 'site_D', },
    ]

    geo_info = GeographicInfo(latitude=42, longitude=69)

    return [
        db_accessor.create(Site(geographic_info=geo_info, **data))
        for data in sites_data]


def _create_buildings(site_ids):
    buildings_data = [
        {'name': 'building_A', 'kind': 'Hospital', 'area': 6900,
         'site_id': site_ids[0]},
        {'name': 'building_B', 'kind': 'Hospital', 'area': 789456,
         'site_id': site_ids[0]},
        {'name': 'building_C', 'kind': 'House', 'area': 420,
         'site_id': site_ids[1]},
        {'name': 'building_D', 'kind': 'Hospital', 'area': 987654,
         'site_id': site_ids[3]},
    ]

    return [db_accessor.create(Building(**data)) for data in buildings_data]


def _create_floors(building_ids):
    floors_data = [
        {'name': 'floor_A', 'kind': 'Ground', 'level': 0,
         'building_id': building_ids[0]},
        {'name': 'floor_B', 'kind': 'Ground', 'level': 0,
         'building_id': building_ids[0]},
        {'name': 'floor_C', 'kind': 'Floor', 'level': -2,
         'building_id': building_ids[2]},
        {'name': 'floor_D', 'kind': 'Subterranean', 'level': 7,
         'building_id': building_ids[3]},
    ]

    spatial_info = SpatialInfo(area=42, max_height=2.4)

    return [
        db_accessor.create(Floor(spatial_info=spatial_info, **data))
        for data in floors_data]


def _create_spaces(floor_ids):
    spaces_data = [
        {'name': 'space_A', 'kind': 'Cafeteria', 'floor_id': floor_ids[0]},
        {'name': 'space_B', 'kind': 'Toilets', 'floor_id': floor_ids[0]},
        {'name': 'space_C', 'kind': 'Toilets', 'floor_id': floor_ids[2]},
        {'name': 'space_D', 'kind': 'Office', 'floor_id': floor_ids[3]},
    ]

    occ = SpaceOccupancy(nb_permanents=0, nb_max=2)
    spat = SpatialInfo(area=10, max_height=1.9)

    return [
        db_accessor.create(Space(occupancy=occ, spatial_info=spat, **data))
        for data in spaces_data]


def _create_zones(building_ids, spaces):
    nb_spaces = randint(0, len(spaces))
    z_spaces = [str(space_id) for space_id in spaces[:nb_spaces]]

    zones_data = [
        {'name': 'zone_A', 'zones': [], 'spaces': z_spaces,
         'building_id': building_ids[0]},
        {'name': 'zone_B', 'zones': None, 'spaces': z_spaces,
         'building_id': building_ids[0]},
    ]

    result = [db_accessor.create(Zone(**data)) for data in zones_data]

    zones_data = [
        {'name': 'zone_C', 'zones': [result[0]], 'spaces': z_spaces,
         'building_id': building_ids[2]},
        {'name': 'zone_D', 'zones': result, 'spaces': z_spaces,
         'building_id': building_ids[3]},
    ]

    result.extend([db_accessor.create(Zone(**data)) for data in zones_data])
    return result


def _create_facades(building_ids, spaces):
    facades_data = [
        {'name': 'facade_A', 'building_id': building_ids[0]},
        {'name': 'facade_B', 'building_id': building_ids[0]},
        {'name': 'facade_C', 'building_id': building_ids[2]},
        {'name': 'facade_D', 'building_id': building_ids[3]},
    ]

    nb_spaces = randint(0, len(spaces))
    f_spaces = [str(space_id) for space_id in spaces[:nb_spaces]]

    f_surface_info = SurfaceInfo(area=10)

    return [
        db_accessor.create(Facade(
            spaces=f_spaces, orientation='South_West', windows_wall_ratio=0.3,
            surface_info=f_surface_info, **data))
        for data in facades_data]


def _create_slabs(building_ids, floors):
    slabs_data = [
        {'name': 'slab_A', 'kind': 'BaseSlab', 'building_id': building_ids[0]},
        {'name': 'slab_B', 'kind': 'FloorSlab',
         'building_id': building_ids[0]},
        {'name': 'slab_C', 'building_id': building_ids[2]},
        {'name': 'slab_D', 'kind': 'Roof', 'building_id': building_ids[3]},
    ]

    nb_floors = randint(0, len(floors))
    f_floors = [str(floor_id) for floor_id in floors[:nb_floors]]

    f_surface_info = SurfaceInfo(area=100)

    return [
        db_accessor.create(Slab(
            floors=f_floors, surface_info=f_surface_info, **data))
        for data in slabs_data]


def _create_windows(facade_ids):
    windows_data = [
        {'name': 'window_A', 'covering': 'Curtain',
         'facade_id': facade_ids[0]},
        {'name': 'window_B', 'covering': 'Blind',
         'facade_id': facade_ids[0]},
        {'name': 'window_C', 'covering': 'Blind',
         'facade_id': facade_ids[2]},
        {'name': 'window_D', 'covering': 'Shade',
         'facade_id': facade_ids[3]},
    ]

    spat = SurfaceInfo(area=3.1)
    # OrientedSpatialInfo(area=3.1, orientation='South_East')

    return [
        db_accessor.create(Window(surface_info=spat, **data))
        for data in windows_data]


def _create_occupants():
    occupants_data = [
        {'token_id': '123456', 'gender': 'Male',
         'age_category': AgeCategory.ac_65.name, },
        {'token_id': '789101', 'gender': 'Female',
         'age_category': AgeCategory.ac_35_44.name, },
        {'token_id': '121314', 'gender': 'Male',
         'age_category': AgeCategory.ac_25_34.name, },
        {'token_id': '151618', 'gender': 'Female',
         'age_category': AgeCategory.ac_65.name, },
    ]

    workspace = OccupantWorkspace(kind='office', desk_location_window='far')

    return [
        db_accessor.create(Occupant(workspace=workspace, **data))
        for data in occupants_data]


def _create_comforts(occupant_id):
    comforts_data = [
        {'description': 'comfort version A', },
        {'description': 'comfort version B', },
        {'description': 'comfort version C', },
        {'description': 'comfort version D', },
    ]

    # use `time.sleep` to be sure that all time attributes are different
    for cur_comfort in comforts_data:
        cur_comfort['time'] = dt.datetime.utcnow()
        time.sleep(0.01)

    comfort_perceptions = [
        ComfortPerception(
            aspect_type='air_humidity', perception=3, satisfaction=2,
            preference='lower'),
    ]

    return [
        db_accessor.create(Comfort(
            occupant_id=occupant_id, perceptions=comfort_perceptions, **data))
        for data in comforts_data]


def _create_sensors(site_ids, building_ids, floor_ids, space_ids):
    localization = [
        Localization(site_id=site_ids[0]),
        Localization(building_id=building_ids[0]),
        Localization(space_id=space_ids[2]),
        Localization(floor_id=floor_ids[3]),
    ]
    sensors_data = [
        {'name': 'sensor_A', 'description': 'sensor version A'},
        {'name': 'sensor_B', 'description': 'sensor version B',
         'static': 'False'},
        {'name': 'sensor_C', 'description': 'sensor version C'},
        {'name': 'sensor_D', 'description': 'sensor version D'},
    ]

    return [
        db_accessor.create(Sensor(**data, localization=localization[idx]))
        for idx, data in enumerate(sensors_data)]


def _create_measures(device_ids, space_ids):
    measures_data = [
        {'description': 'measure version A', 'unit': 'DegreeCelsius',
         'observation_type': 'Temperature', 'medium': 'Air',
         'sensor_id': device_ids[0]},
        {'description': 'measure version B', 'unit': 'DegreeFahrenheit',
         'observation_type': 'Temperature', 'medium': 'Water',
         'sensor_id': device_ids[0], 'associated_locations': [space_ids[0]]},
        {'description': 'measure version C', 'unit': 'DegreeCelsius',
         'observation_type': 'Temperature', 'medium': 'Water',
         'sensor_id': device_ids[2]},
        {'description': 'measure version D', 'unit': 'DegreeFahrenheit',
         'observation_type': 'Temperature', 'medium': 'Air',
         'sensor_id': device_ids[3]},
    ]

    measures = [Measure(**data) for data in measures_data]
    for idx, measure in enumerate(measures):
        measure.add_external_id('Test_{}'.format(idx))

    return [db_accessor.create(m) for m in measures]


def _create_services(site_ids):
    services_data = [
        {'name': 'service_A', 'url': 'http://hit2gap.eu/fdd',
         'site_ids': [site_ids[0]]},
        {'name': 'service_B', 'url': 'http://hit2gap.eu/forecasting',
         'site_ids': [site_ids[0], site_ids[3]], 'has_frontend': True},
        {'name': 'service_C', 'url': 'http://hit2gap.eu/serviceC',
         'site_ids': [site_ids[2]]},
        {'name': 'service_D', 'url': 'http://hit2gap.eu/serviceD',
         'site_ids': [site_ids[3]], 'has_frontend': True},
    ]
    return [db_accessor.create(Service(**data)) for data in services_data]


def _create_models(service_ids):
    params = [[Parameter('ar', 1), Parameter('I', 2), Parameter('MA', 0)],
              [Parameter('gamma', 0.543)]]
    models_data = [
        {
            'name': 'ARIMA #1', 'service_id': service_ids[0],
            'description': 'A sample model #1', 'parameters': params[0],
        },
        {
            'name': 'SRV #1', 'service_id': service_ids[1],
            'description': 'A sample model #2', 'parameters': params[1],
        }
    ]
    return [db_accessor.create(Model(**data)) for data in models_data]


def _create_event_outputs(service_ids, model_ids):
    outputs_data = [
        {'module_id': service, 'model_id': model}
        for service, model in zip(service_ids, model_ids)
    ]
    return [db_accessor.create(OutputEvent(**data)) for data in outputs_data]


def _create_timeseries_outputs(site_ids, service_ids, model_ids):
    outputs_data = [
        {
            'localization': site,
            'module_id': service,
            'model_id': model,
            'external_id': external_id,
            'values_desc': ValuesDescription(**{
                'kind': 'Temperature',
                'unit': 'DegreeCelsius',
                'sampling': samp,
            })

        }
        for site, service, model, samp, external_id in zip(
            site_ids, service_ids, model_ids, [20, 40],
            ['OutputExtID_1', 'OutputExtID_2',
             'OutputExtID_3', 'OutputExtID_4'])
    ]
    return [db_accessor.create(OutputTimeSeries(**data))
            for data in outputs_data]


def _create_outputs(site_ids, service_ids, model_ids):
    return (
        _create_event_outputs(service_ids, model_ids) +
        _create_timeseries_outputs(site_ids, service_ids, model_ids)
    )


def _create_ifc_files(request):
    ifc_files_data = [
        {'original_file_name': 'file_A.ifc', 'file_name': 'file_A.ifc'},
        {'original_file_name': 'file_B.ifc', 'file_name': 'file_B.ifc'},
        {'original_file_name': 'file_C.ifc', 'file_name': 'file_C.ifc'},
        {'original_file_name': 'file_D.ifc', 'file_name': 'file_D.ifc'},
    ]

    ifc_files = {
        db_accessor.create(IFCFile(**data)): data['file_name']
        for data in ifc_files_data}

    fs_mgr = FileStorageMgr(request.cls.config.FILE_STORAGE_DIR)
    for ifc_file_id in ifc_files:
        _, data_stream = ifc_file_data_stream()
        fs_mgr.add(ifc_file_id, ifc_files[ifc_file_id], data_stream)

    return ifc_files


def _create_occupant_users(request):
    occupant_users_data = [
        {'login_id': generate_login_id(), 'password': generate_pwd()},
    ]

    security_mgr = SecurityManager(request.cls.config.SECURITY_STORAGE_DIR)
    occ_uaccs = [
        security_mgr.create_occupant(uid=u_data['login_id'])
        for u_data in occupant_users_data
    ]

    return [(uacc.uid, clear_pwd) for uacc, clear_pwd in occ_uaccs]


def _create_users(request, site_ids):
    site_ids = [str(site_id) for site_id in site_ids]
    module_users_data = [
        {'uid': 'bemsvrapp-input-owm', 'pwd': None, 'user_type': 'machine',
         'roles': ['module_data_provider'], 'sites': ['*']},
        {'uid': 'bemsvrapp-cleaning-timeseries', 'pwd': None,
         'user_type': 'machine', 'roles': ['module_data_processor'],
         'sites': ['*']},
        {'uid': 'multi-site', 'pwd': None, 'user_type': 'user',
         'roles': ['building_manager'], 'sites': site_ids[:2]},
        {'uid': 'app-mono-site', 'pwd': None, 'user_type': 'machine',
         'roles': ['module_data_processor'], 'sites': site_ids[-1:]},
    ]

    # create user accounts
    uaccs = {}
    for u_data in module_users_data:
        uacc = UserAccount(**u_data)
        uacc._password = u_data['pwd']
        uaccs[uacc.uid] = uacc

    # store user accounts in file
    security_dir = Path(request.cls.config.SECURITY_STORAGE_DIR)
    uacc_filepath = security_dir / SecurityManager._USER_ACCOUNTS_FILE
    SecurityManager.save_to_file(str(uacc_filepath), uaccs)

    return [uacc for uacc in uaccs.values()]


@pytest.fixture(params=[{}])
def init_db_data(request, drop_db):
    """Create data in database"""

    def _get_param(param_name, default_value=False):
        if request is not None and isinstance(request.param, dict):
            return request.param.get(param_name, default_value)
        return default_value

    db_data = {}

    if _get_param('gen_sites', True) or _get_param('gen_outputs'):
        db_data['sites'] = _create_sites()

        if _get_param('gen_buildings', True):
            db_data['buildings'] = _create_buildings(db_data['sites'])

    if db_data.get('buildings') and _get_param('gen_floors'):
        db_data['floors'] = _create_floors(db_data['buildings'])

    if db_data.get('floors') and _get_param('gen_spaces'):
        db_data['spaces'] = _create_spaces(db_data['floors'])

    if db_data.get('spaces') and _get_param('gen_zones'):
        db_data['zones'] = _create_zones(
            db_data['buildings'], db_data['spaces'])

    if db_data.get('spaces') and _get_param('gen_facades'):
        db_data['facades'] = _create_facades(
            db_data['buildings'], db_data['spaces'])

    if db_data.get('floors') and _get_param('gen_slabs'):
        db_data['slabs'] = _create_slabs(
            db_data['buildings'], db_data['floors'])

    if db_data.get('facades') and _get_param('gen_windows'):
        db_data['windows'] = _create_windows(db_data['facades'])

    if _get_param('gen_occupants'):
        db_data['occupants'] = _create_occupants()

    if _get_param('gen_sensors'):
        if db_data.get('floors') is None:
            db_data['floors'] = _create_floors(db_data['buildings'])
        if db_data.get('spaces') is None:
            db_data['spaces'] = _create_spaces(db_data['floors'])
        db_data['sensors'] = _create_sensors(
            db_data['sites'], db_data['buildings'], db_data['floors'],
            db_data['spaces'])

    if db_data.get('sensors') and db_data.get('spaces') and\
            _get_param('gen_measures'):
        db_data['measures'] = _create_measures(
            db_data['sensors'], db_data['spaces'])

    if (_get_param('gen_services') or _get_param('gen_models') or
            _get_param('gen_outputs')):
        db_data['services'] = _create_services(db_data['sites'])

    if _get_param('gen_models') or _get_param('gen_outputs'):
        db_data['models'] = _create_models(db_data['services'])

    if _get_param('gen_outputs'):
        db_data['outputs'] = _create_outputs(
            db_data['sites'], db_data['services'], db_data['models'])

    if _get_param('gen_ifc_files'):
        db_data['ifc_files'] = _create_ifc_files(request)

    if _get_param('gen_comforts'):
        occupant_id = db_data['occupants'][0]
        db_data['comforts'] = _create_comforts(occupant_id)

    if _get_param('gen_occupant_users', True):
        db_data['occupant_users'] = _create_occupant_users(request)

    if _get_param('gen_users', True):
        db_data['users'] = _create_users(request, db_data['sites'])

    return db_data


def ifc_file_obj():
    """Return a sample IFC file object"""
    file_name, file_content = ifc_file_data()
    return file_name, file_content, build_file_obj(file_name, file_content)


@pytest.fixture(name='ifc_file_obj')
def ifc_file_obj_fixture():
    """Fixture to return a sample IFC file object"""
    return ifc_file_obj()


def ifc_zip_file_obj(file_ext):
    """Return a sample IFC zipped file object"""
    zip_file_name, zip_file_data = ifc_zip_file_data(file_ext)
    return zip_file_name, build_file_obj(zip_file_name, zip_file_data)


@pytest.fixture(name='ifc_zip_file_obj', params=['.zip'])
def ifc_zip_file_obj_fixture(request):
    """Fixture to return a sample IFC zipped file object"""
    return ifc_zip_file_obj(request.param)


def ifc_multi_zip_file_obj(file_ext):
    """Return many IFC samples zipped in one file object"""
    zip_file_name, zip_file_data = ifc_multi_zip_file_data(file_ext)
    return zip_file_name, build_file_obj(zip_file_name, zip_file_data)


@pytest.fixture(name='ifc_multi_zip_file_obj', params=['.zip'])
def ifc_multi_zip_file_obj_fixture(request):
    """Fixture to return many IFC samples zipped in one file object"""
    return ifc_multi_zip_file_obj(request.param)


def generate_certificate_data(cn_data='bemsvrapp-cleaning-timeseries'):
    """Generate a sample of valid certificate data."""
    return 'CN={},AND=other_stuff'.format(cn_data)


@pytest.fixture(params=['bemsvrapp-cleaning-timeseries'])
def certificate_data(request):
    """Return a sample of valid data for certificate authentication."""
    return generate_certificate_data(request.param)
