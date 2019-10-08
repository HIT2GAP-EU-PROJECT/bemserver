"""Timeseries basics services - Utils for helping building timeseries views."""

from bemserver.models import (
    Sensor, Measure, OutputTimeSeries, Site, Building, Floor, Zone, Space)
from bemserver.models.timeseries.exceptions import (
    TimeseriesUnitConversionError)

from ..api.extensions.auth import verify_scope
from ..api.extensions.rest_api import abort
from ..api.extensions.database import db_accessor

from ..api.views.timeseries import tsio


def get_timeseries_by_id_resample(
        ts_id, t_start, t_end, target_unit, freq, aggregation):
    """Get Timeseries by id and resample it. Return resampled Timeseries."""
    item = get_item_checked(ts_id)
    # Check if unit arguments are valid
    is_valid_unit(item['unit'], target_unit)
    # Get timeseries
    ret_ts = get_timeseries_by_item(item, t_start, t_end)
    # Convert timeseries unit
    ret_ts = convert_timeseries_unit(ret_ts, item['unit'], target_unit)
    # Resample timeseries
    ret_ts.resample(freq, aggregation)
    return ret_ts


def get_item_checked(timeseries_id):
    """Get item and check permission to use it."""
    item = _get_item_or_404(timeseries_id)
    # permissions checks
    verify_scope(sites=[item['site_id']])
    # Compatibility with ugly onto stub
    return item


def get_timeseries_by_item(item, t_start, t_end):
    """Get Timeserie from item element."""
    ts_mgr = tsio.get_timeseries_manager()
    return ts_mgr.get(
        item['site_id'], item['ts_id'], t_start=t_start, t_end=t_end)


def is_valid_unit(source_unit, target_unit):
    """Check if source / target unit is valid"""
    if target_unit is not None and source_unit is None:
        # conversion can not be done
        abort(422, errors={'unit': [
            'Unit conversion not allowed: timeseries unit not defined.']})


def convert_timeseries_unit(timeseries, source_unit=None, target_unit=None):
    """Convert Timeseries unit. Return converted Timeseries."""
    ret_ts = timeseries
    # values conversion part
    if target_unit is not None:
        try:
            ret_ts.convert_unit(source_unit, target_unit)
        except TimeseriesUnitConversionError as exc:
            abort(422, exc=exc, errors={'unit': [str(exc)]})
    return ret_ts


def _get_item_or_404(timeseries_id):
    # A. search in measures
    #  parent site can be reached through sensor
    # B. if not found, search in outputs
    #  parent site can be reached through service
    # C. return a generic response:
    #   {
    #       'kind': ...,
    #       'ts_id': ...,
    #       'site_id': ...,
    #       'unit': ...,
    #   }

    clean = False
    # Ugly hack to keep compatibility with ugly ontology stub for @clean TS
    if timeseries_id.endswith('@clean'):
        clean = True
        timeseries_id = timeseries_id[:-6]

    result = {'kind': 'measure'}
    # A. get measure from timeseries_id (measure's external_id)
    sieve = {'external_id': timeseries_id}
    item = db_accessor.get_list(Measure, sieve)
    if not item:
        # B. get output timeseries from timeseries_id (output's external_id)
        result['kind'] = 'output'
        item = db_accessor.get_list(OutputTimeSeries, sieve)
    if not item:
        abort(404)

    # build response with item data
    item = item[0]
    result['ts_id'] = item.external_id + ('@clean' if clean else '')
    if result['kind'] == 'measure':
        result['unit'] = item.unit
        result['site_id'] = db_accessor.get_parent(Sensor, item.sensor_id)
    else:
        result['unit'] = item.values_desc.unit
        # TODO: replace with BuildingStructuralElement? use inheritance
        result['site_id'] = db_accessor.get_parent_many_classes(
            [Space, Zone, Floor, Building, Site], item.localization
        )

    return result
