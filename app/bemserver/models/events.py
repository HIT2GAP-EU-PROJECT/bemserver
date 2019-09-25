"""Events model"""

import uuid

import sqlalchemy as sa
from sqlalchemy_utils.types.uuid import UUIDType

from bemserver.database.relational import db

from bemserver.tools.custom_enum import HierarchyEnum


LEVEL_TYPES = ('INFO', 'WARNING', 'ERROR', 'CRITICAL')


class EventCategory(HierarchyEnum):
    """Event categories and subcategories"""

    # Comfort
    comfort = ('Comfort issue', )
    comfort_temp_high = ('temperature too high', 'comfort')
    comfort_temp_low = ('temperature too low', 'comfort')
    comfort_rh_high = ('relative humidity too high', 'comfort')
    comfort_rh_low = ('relative humidity too low', 'comfort')
    comfort_visual = ('visual issue', 'comfort')
    comfort_acoustic = ('acoustic issue', 'comfort')

    # Indoor Air Quality
    iaq = ('Bad indoor air quality', )
    iaq_co2_high = ('CO2 too high', 'iaq')
    iaq_pmv = ('predicted mean vote', 'iaq')

    # Energy consumption
    energy_cons = ('Abnormal energy consumption', )
    energy_cons_heating = ('heating', 'energy_cons')
    energy_cons_cooling = ('cooling', 'energy_cons')
    energy_cons_lighing = ('lighing', 'energy_cons')
    energy_cons_ventilation = (
        'Energy consumption: ventilation', 'energy_cons')
    energy_cons_plug_load = ('plug load', 'energy_cons')

    # Energy production
    energy_production = ('Information on enregy production',)

    # Operating conditions
    operating_cond = ('Abnormal operating conditions', )
    operating_cond_scheduling = (
        'scheduling', 'operating_cond')
    operating_cond_device = (
        'device', 'operating_cond')

    # Measures
    measures = ('Abnormal measure values', )
    measures_missing = ('missing value', 'measures')
    measures_range = ('value out of range', 'measures')
    measures_inconsistency = ('inconsistency', 'measures')


class Event(db.Model):
    """Event model class"""

    id = sa.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    # Application and model ID
    application = sa.Column(sa.String)
    model = sa.Column(sa.String)

    execution_timestamp = sa.Column(sa.DateTime)

    # Location
    site_id = sa.Column(sa.String)
    building_id = sa.Column(sa.String)
    floor_id = sa.Column(sa.String)
    space_id = sa.Column(sa.String)
    sensor_ids = sa.Column(sa.String())

    level = sa.Column(sa.String)
    category = sa.Column(sa.String)

    # Timeframe
    start_time = sa.Column(sa.DateTime)
    end_time = sa.Column(sa.DateTime)

    reliability = sa.Column(sa.Float)

    description = sa.Column(sa.String)
