"""Api measures module schemas"""

import marshmallow as ma

from bemserver.models.timeseries import Timeseries

from ...extensions.rest_api import rest_api
from ...extensions import marshmallow as ext_ma


class TimeseriesUnitConversionQueryArgsSchema(ma.Schema):
    """Timeseries unit conversion GET/PATCH query parameters schema."""

    class Meta:
        """Schema Meta properties."""
        strict = True

    unit = ma.fields.String(
        description='''Unit of the timeseries values.
        The list is taken from the [Pint library](
        https://github.com/hgrecco/pint/blob/master/pint/default_en.txt).
        For convenience, we added `'percent'`, `'permille'` and `'ppm'` units.
        ''',
        example='degC',
    )


class TimeseriesQueryArgsSchema(TimeseriesUnitConversionQueryArgsSchema):
    """Timeseries values GET query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        ordered = True

    start_time = ext_ma.fields.StrictDateTime(
        required=True,
        attribute='t_start',
        description='Initial date',
        example='2017-01-01T00:00:00'
    )
    end_time = ext_ma.fields.StrictDateTime(
        required=True,
        attribute='t_end',
        description='End date (excluded from the interval)',
        example='2017-01-03T00:00:00'
    )


class TimeseriesStatsQueryArgsSchema(ma.Schema):
    """Timeseries stats GET query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        ordered = True

    start_time = ext_ma.fields.StrictDateTime(
        attribute='t_start',
        description='Initial date',
        example='2017-01-01T00:00:00'
    )

    end_time = ext_ma.fields.StrictDateTime(
        attribute='t_end',
        description='End date (excluded from the interval)',
        example='2017-01-03T00:00:00'
    )


class TimeseriesResampleQueryArgsSchema(TimeseriesQueryArgsSchema):
    """Timeseries values GET query parameters schema"""

    freq = ma.fields.String(
        required=True,
        description='New sampling frequency',
        validate=ma.validate.OneOf(Timeseries.AGG_FREQUENCIES.keys()),
        example='month'
    )

    aggregation = ma.fields.String(
        required=True,
        description=
        '''Aggregation operation to apply. When performing
           downsampling (for instance, daily resampling of hourly data),
           the output timeseries are obtained by aggregating data (i.e.
           either sum, mean, min or max).''',
        validate=ma.validate.OneOf(Timeseries.AGG_OPERATIONS),
        example='sum'
    )


class TimeseriesAggregateQueryArgsSchema(TimeseriesQueryArgsSchema):
    """Timeseries aggregate GET query parameters schema"""

    freq = ma.fields.String(
        required=True,
        description='''New sampling frequency. **Only downsampling can be
        performed. Upsampling could lead to duplicated values.**''',
        validate=ma.validate.OneOf(Timeseries.AGG_FREQUENCIES.keys()),
        example='month'
    )

    resampling_method = ma.fields.String(
        attribute='rs_agg',
        required=True,
        description=(
            'Aggregation method to apply for resampling data. For instance, '
            'minutely sampled data can be hourly resampled by summing values. '
            'It does downsampling but no upsampling.'),
        validate=ma.validate.OneOf(Timeseries.AGG_OPERATIONS),
        example='sum'
    )

    ts_ids = ma.fields.List(
        ma.fields.String,
        required=True,
        description='''The list of ID for the timeseries to aggregate.''',
    )

    operation = ma.fields.String(
        attribute='ts_agg',
        required=True,
        description="""Aggregation method to apply for aggregating timeseries.

+ **sum**: on multiple timeseries will return a single time series made of
the summed values at each time stamp.
+ **mean**: on multiple timeseries will return a single time series made of
the mean value from values at each time stamp.
+ **max**: on multiple timeseries will return a single time series made of
the maximum value from these timeseries at time stamp.
+ **min**: on multiple timeseries will return a single time series made of
the minumum value from these timeseries at time stamp.""",
        validate=ma.validate.OneOf(Timeseries.AGG_OPERATIONS),
        example='max'
    )


@rest_api.definition('TimeseriesValue')
class TimeseriesValueSchema(ma.Schema):
    """Timeseries value schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        ordered = True

    timestamp = ext_ma.fields.StrictDateTime(
        required=True,
        description="Value time",
        example='2017-01-01T00:00:00'
    )

    value = ma.fields.Float(
        required=True,
        description="Value",
        example='3.141592653589793'
    )

    update_ts = ext_ma.fields.StrictDateTime(
        dump_only=True,
        description="Value update time",
        example='2017-01-03T00:00:00'
    )

    quality = ma.fields.Float(
        validate=ma.validate.Range(min=0, max=1),
        description="Value quality rate",
        missing=1,
        example='1'
    )


@rest_api.definition('Timeseries')
class TimeseriesSchema(ma.Schema):
    """Timeseries schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    data = ma.fields.Nested(
        TimeseriesValueSchema, many=True,
        required=True,
    )


@rest_api.definition('TimeseriesStats')
class TimeseriesStatsSchema(ma.Schema):
    """TimeseriesStats schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        ordered = True

    count = ma.fields.Integer(
        description='Number of values in specified period',
        example='42'
    )
    start_time = ext_ma.fields.StrictDateTime(
        attribute='start',
        description='Date of first value in specified period',
        example='2017-01-01T00:00:00'
    )
    end_time = ext_ma.fields.StrictDateTime(
        attribute='end',
        description='Date of last value in specified period',
        example='2017-01-03T00:00:00'
    )
    update_ts = ext_ma.fields.StrictDateTime(
        description='Date of latest update',
        example='2018-01-01T00:00:00'
    )
