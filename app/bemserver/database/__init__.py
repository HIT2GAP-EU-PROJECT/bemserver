"""Database module initialization"""

from bemserver.models import (
    Site, Building, Floor, Space, Zone, Facade, Slab, Window, Sensor, Measure,
    Service, Model, Output, OutputEvent, OutputTimeSeries)
from bemserver.database.ontology.manager import (
    ontology_manager_factory)

from .dbaccessor import DBAccessor  # noqa
from .db_mock import SORT_ASCENDING, SORT_DESCENDING  # noqa

from .db_site import SiteDB
from .db_building import BuildingDB
from .db_quantity import QuantityDB  # noqa
from .db_floor import FloorDB
from .db_space import SpaceDB
from .db_zone import ZoneDB
from .db_wall import FacadeDB
from .db_slab import SlabDB
from .db_window import WindowDB
from .db_sensor import SensorDB
from .db_measure import MeasureDB
from .db_service import ServiceDB
from .db_model import ModelDB
from .db_output import OutputDB


def init_handlers(url=None):
    if url:
        ontology_manager_factory.open(url)
    return {
        Site: SiteDB(),
        Building: BuildingDB(),
        Floor: FloorDB(),
        Space: SpaceDB(),
        Zone: ZoneDB(),
        Facade: FacadeDB(),
        Slab: SlabDB(),
        Window: WindowDB(),
        Sensor: SensorDB(),
        Measure: MeasureDB(),
        Service: ServiceDB(),
        Model: ModelDB(),
        Output: OutputDB(),
        OutputEvent: OutputDB(),
        OutputTimeSeries: OutputDB(),
    }
