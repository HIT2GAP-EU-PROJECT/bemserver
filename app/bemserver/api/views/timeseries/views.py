"""Api Timeseries module views"""

from flask import current_app
from flask.views import MethodView

from bemserver.basicservices.timeseries import (
    get_timeseries_by_id_resample, get_item_checked, get_timeseries_by_item,
    is_valid_unit, convert_timeseries_unit)

from bemserver.models.timeseries.exceptions import (
    TimeseriesUnitConversionError)

from . import bp as api

from .schemas import (
    TimeseriesSchema, TimeseriesStatsSchema,
    TimeseriesQueryArgsSchema, TimeseriesResampleQueryArgsSchema,
    TimeseriesStatsQueryArgsSchema, TimeseriesUnitConversionQueryArgsSchema,
    TimeseriesAggregateQueryArgsSchema)
from . import tsio

from ...extensions.rest_api import abort
from ...extensions.rest_api.doc_responses import build_responses
from ...extensions.auth import auth_required
from ...extensions.limiter import limiter

from ....models import Timeseries


@api.route('/<string:timeseries_id>')
class TimeseriesById(MethodView):
    """Timeseries resources endpoint"""

    @auth_required(roles=[
        'building_manager', 'module_data_provider', 'module_data_processor'])
    @limiter.limit(1)
    @api.doc(
        summary='Get values for a timeseries',
        description='''Given a measure ID, returns the list of pairs
        (timestamp, value) for this measure. **Beware that, if the time range
        is too wide in the request, this can take a LONG time!**
        Unit conversion can be performed for a request.<br>
        *Example:* `/timeseries/my_timeseries_id?start_time=2019-06-18T00:00:00
        &end_time=2019-06-19T00:00:00`
        ''',
        responses=build_responses(
            [200, 404, 422, 500], schemas={200: TimeseriesSchema})
    )
    @api.arguments(TimeseriesQueryArgsSchema, location='query')
    @api.response(disable_etag=True)
    def get(self, args, timeseries_id):
        item = get_item_checked(timeseries_id)
        # Check if unit arguments are valid
        target_unit = args.get('unit')
        is_valid_unit(item['unit'], target_unit)
        # Get timeseries
        t_start, t_end = args['t_start'], args['t_end']
        ret_ts = get_timeseries_by_item(item, t_start, t_end)
        # Convert timeseries unit
        ret_ts = convert_timeseries_unit(ret_ts, item['unit'], target_unit)
        return {'data': tsio.tsdump(ret_ts, to_isotime=True)}

    @auth_required(roles=['module_data_provider', 'module_data_processor'])
    @limiter.limit(1)
    @api.doc(
        summary='''Set values for a timeseries.''',
        description=('''This operation is used to feed a timeseries with some
                     values in the form of pairs (timestamp, value).<br>
                     If some values are already stored for some or all of the
                     timestamps given, former values will be replaced with
                     values in the request.'''),
        responses=build_responses([204, 404, 422, 500])
    )
    @api.arguments(TimeseriesSchema)
    @api.arguments(TimeseriesUnitConversionQueryArgsSchema, location='query')
    @api.response(code=204, disable_etag=True)
    def patch(self, data, args, timeseries_id):
        item = get_item_checked(timeseries_id)
        # Check if unit conversion arguments are valid
        source_unit = args.get('unit')
        if source_unit is not None and item['unit'] is None:
            # conversion can not be done
            abort(422, errors={'unit': [
                'Unit conversion not allowed: timeseries unit not defined.']})
        # Load data
        current_app.logger.info('Setting values for timeseries "%s/%s"',
                                item['site_id'], item['ts_id'])
        ts_mgr = tsio.get_timeseries_manager()
        data_ts = tsio.tsload(data['data'])
        # Convert values to asked unit
        if source_unit is not None:
            try:
                data_ts.convert_unit(source_unit, item['unit'])
            except TimeseriesUnitConversionError as exc:
                abort(422, exc=exc, errors={'unit': [str(exc)]})
        ts_mgr.set(item['site_id'], item['ts_id'], data_ts)

    @auth_required(roles=['module_data_provider', 'module_data_processor'])
    @limiter.limit(1)
    @api.doc(
        summary='Delete values in a timeseries',
        responses=build_responses([204, 404, 422, 500])
    )
    @api.arguments(TimeseriesQueryArgsSchema, location='query')
    @api.response(code=204, disable_etag=True)
    def delete(self, args, timeseries_id):
        item = get_item_checked(timeseries_id)
        current_app.logger.info(
            'Deleting values for timeseries "%s/%s"',
            item['site_id'], item['ts_id'])
        t_start, t_end = args['t_start'], args['t_end']
        ts_mgr = tsio.get_timeseries_manager()
        ts_mgr.delete(item['site_id'], item['ts_id'], t_start, t_end)


@api.route('/<string:timeseries_id>/stats')
@auth_required(roles=[
    'building_manager', 'module_data_provider', 'module_data_processor'])
@limiter.limit(1)
@api.doc(
    summary='Get stats about timeseries',
    description=('''This endpoint returns:

+ value count
+ index/timestamp of first value
+ index/timestamp of last value.

This can be useful to parse timeseries, i.e. to check whether some new values
can be read.'''),
    responses=build_responses([200, 404, 422, 500])
)
@api.arguments(TimeseriesStatsQueryArgsSchema, location='query')
@api.response(TimeseriesStatsSchema)
def timeseries_by_id_stats(args, timeseries_id):
    item = get_item_checked(timeseries_id)
    # Get timeseries
    t_start, t_end = args.get('t_start', None), args.get('t_end', None)
    ret_ts = get_timeseries_by_item(item, t_start, t_end)
    return ret_ts.stats()


@api.route('/<string:timeseries_id>/resample')
@auth_required(roles=[
    'building_manager', 'module_data_provider', 'module_data_processor'])
@limiter.limit(1)
@api.doc(
    summary='Resample a timeseries',
    description=('''This endpoint returns the data resampled at a given
                 frequency. It does downsampling but no upsampling:
                 the frequency passed as parameter need to be higher that the
                 original frequency of the timeseries.<br>Data are then
                 aggregated according to the operation specified in the
                 request.<br><br>For instance, an hourly measured energy
                 consumption can be transformed into a daily energy consumption
                 with parameters `'day`' and `'sum`'<br>A measure of ambient
                 temperature collected every second, can be gathered at an
                 hourly frequency with parameters `'hour`' and `'mean`'.'''),
    responses=build_responses(
        [200, 404, 422, 500], schemas={200: TimeseriesSchema})
)
@api.arguments(TimeseriesResampleQueryArgsSchema, location='query')
@api.response(disable_etag=True)
def timeseries_by_id_resample(args, timeseries_id):
    t_start, t_end = args['t_start'], args['t_end']
    target_unit = args.get('unit')
    freq, aggregation = args['freq'], args['aggregation']
    ret_ts = get_timeseries_by_id_resample(
        timeseries_id, t_start, t_end, target_unit, freq, aggregation)
    return {'data': tsio.tsdump(ret_ts, to_isotime=True)}


@api.route('/aggregate')
@auth_required(roles=[
    'building_manager', 'module_data_provider', 'module_data_processor'])
@limiter.limit(1)
@api.doc(
    summary='Aggregate timeseries data.',
    description=('''This endpoint returns multiple timeseries aggregated. Data
                 are aggregated according to the method (operation) specific in
                 the requrest and resampled at a given frequency with specified
                 method (resampling_method).<br>
                 *Example* If `measure1` and `measure2` are both temperature
                 measures in some room, one can get the average temperature in
                 the room based on these two measures:<br>
                 `/timeseries/aggregate/?start_time=DATE1&end_time=DATE2&
                 freq=min&ts_ids=['measure1','measure2']&operation=mean`'''),
    responses=build_responses(
        [200, 404, 422, 500], schemas={200: TimeseriesSchema})
)
@api.arguments(TimeseriesAggregateQueryArgsSchema, location='query')
@api.response(disable_etag=True)
def timeseries_aggregate(args):
    ts_ids = args['ts_ids']
    t_start, t_end = args['t_start'], args['t_end']
    target_unit = args.get('unit')
    freq, aggregation = args['freq'], args['rs_agg']

    timeserie_list = [
        get_timeseries_by_id_resample(
            ts_id, t_start, t_end, target_unit, freq, aggregation)
        for ts_id in ts_ids
    ]
    operation = args['ts_agg']
    ret_ts = Timeseries.aggregate(timeserie_list, operation)
    return {'data': tsio.tsdump(ret_ts, to_isotime=True)}
