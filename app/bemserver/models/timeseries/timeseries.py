"""Timeseries manipulation model"""

import numpy as np
import pandas as pd

from bemserver.tools import units

from .exceptions import (
    TimeseriesInvalidIndexTypeError,
    TimeseriesMissingColumnError, TimeseriesInvalidColumnsError,
    TimeseriesUnitConversionError)


class Timeseries():
    """Object storing Timeseries.

    The internal DataFrame is of the form:
    - index: timestamps as datetime
    - data: data as float
    - quality: quality indicator in [0; 1] as float
    - update_ts: update time as datetime
    """

    # TODO: change 'index' into 'timestamps'? Retro-compatibility issues?
    TIMESTAMPS_COL = 'index'
    DATA_COL = 'data'
    QUALITY_COL = 'quality'
    UPDATE_TIMESTAMP_COL = 'update_ts'

    AGG_FREQUENCIES = {
        'sec': 'S',
        '10sec': '10S',
        '15sec': '15S',
        '30sec': '30S',
        'min': 'T',
        '10min': '10T',
        '15min': '15T',
        '30min': '30T',
        'hour': 'H',
        '3hour': '3H',
        '6hour': '6H',
        '12hour': '12H',
        'day': 'D',
        'week': 'W',
        'month': 'MS',
        '3month': '3MS',
        '6month': '6MS',
        'year': 'YS',
    }

    AGG_OPERATIONS = ('sum', 'mean', 'min', 'max')

    def __init__(self, *, index=None, data=None, quality=None, update_ts=None):
        """
        ..Note:
            Timeseries init follows some rules:
                - data/quality can not be set without index
                - quality can not be set without data
                - update_ts can not be set without data

        :param pandas.DatetimeIndex index: (optional, default None)
            Index values, fills index column in dataframe.
        :param list data: (optional, default None)
            Data values, fills data column in dataframe.
        :param list quality: (optional, default None)
            Quality values, fills quality column in dataframe.
        :param list update_ts: (optional, default None)
            Update timestamps values, fills update_ts column in dataframe.
        :raises TimeseriesMissingColumnError:
            When index is not defined while data/quality is
            or when data is not defined while quality is.
        """
        if index is None and (data is not None or quality is not None):
            raise TimeseriesMissingColumnError(
                '{}/{} is defined but {} is missing.'
                .format(self.DATA_COL, self.QUALITY_COL, self.TIMESTAMPS_COL))

        if data is None and (quality is not None or update_ts is not None):
            raise TimeseriesMissingColumnError(
                '{} is defined but {} is missing.'
                .format(self.QUALITY_COL, self.DATA_COL))

        self._df = self.empty_dataframe()

        if index is not None:
            if data is None:
                data = np.NaN
            if quality is None:
                quality = 1
            if update_ts is None:
                update_ts = pd.NaT

            self._df[Timeseries.DATA_COL] = data
            self._df[Timeseries.QUALITY_COL] = quality
            self._df[Timeseries.UPDATE_TIMESTAMP_COL] = update_ts
            self._df.index = index

            self.validate()

    @property
    def dataframe(self):
        """
        :returns pandas.DataFrame: The timeseries' structured dataframe.
        """
        return self._df

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>(count={count}'
            ', start={start}, end={end}, min={min}, max={max})'
            .format(
                self=self, count=len(self._df),
                start=self._df.index.min(),
                end=self._df.index.max(),
                min=self._df[self.DATA_COL].min(),
                max=self._df[self.DATA_COL].max()))

    @classmethod
    def empty_dataframe(cls):
        """Build an empty Timeseries object.

        :returns pandas.DataFrame: An empty dataframe, timeseries structured.
        """
        dataframe = pd.DataFrame(
            {
                cls.DATA_COL: pd.Series([], dtype='float64'),
                cls.UPDATE_TIMESTAMP_COL: pd.Series(
                    [], dtype='datetime64[ns]'),
                cls.QUALITY_COL: pd.Series([], dtype='float64'),
                cls.TIMESTAMPS_COL: pd.Series([], dtype='datetime64[ns]'),
            },
            index=[])
        dataframe.set_index(cls.TIMESTAMPS_COL, inplace=True)
        return dataframe

    @classmethod
    def from_dataframe(cls, dataframe):
        """Create a timeseries from a DataFrame instance.

        :returns Timeseries: A timeseries pre-loaded with dataframe.
        """
        return Timeseries(
            index=dataframe.get(cls.TIMESTAMPS_COL, dataframe.index),
            data=dataframe.get(cls.DATA_COL),
            quality=dataframe.get(cls.QUALITY_COL),
            update_ts=dataframe.get(cls.UPDATE_TIMESTAMP_COL))

    @classmethod
    def aggregate(cls, timeseries, operation):
        """Aggregate Timeseries objects.

        Aggregate Timeseries objects using provided operation to
        aggregate data column.

        Quality and update timestamp columns are aggregated using mean and max
        respectively.

        :param list timeseries: List of Timeseries object.
        :param str operation: Aggregation operation to apply to data.
            Muse be in AGG_OPERATIONS

        :returns Timeseries: A Timeseries object.
        """
        # Pandas skip nan when calculating mean: mean([np.nan, 2]) return 2
        # http://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.mean.html
        def namean(serie):
            return serie.sum() / serie.size

        concat = pd.concat([ts.dataframe for ts in timeseries], axis=1)
        if concat.empty:
            return Timeseries()

        return Timeseries(
            index=concat.index,
            data=concat[cls.DATA_COL].agg(operation, axis=1),
            quality=concat[cls.QUALITY_COL].agg(namean, axis=1),
            update_ts=concat[cls.UPDATE_TIMESTAMP_COL].agg('max', axis=1))

    def validate(self):
        """Validates timeseries' dataframe structure.

        :raises TimeseriesInvalidIndexTypeError:
            When index type is not valid (pandas.DatetimeIndex expected).
        :raises TimeseriesMissingColumnError:
            When required columns are missing (only data column is required).
        :raises TimeseriesInvalidColumnsError:
            When not allowed columns are found (only data, quality and
            update_ts are accepted).
        """
        # Check index is DatetimeIndex
        if not isinstance(self._df.index, pd.DatetimeIndex):
            raise TimeseriesInvalidIndexTypeError(
                "Invalid index type '{}'. Should be DatetimeIndex."
                .format(type(self._df.index)))

        # Check columns in DataFrame
        required_columns = {self.DATA_COL}
        allowed_columns = {
            self.DATA_COL, self.QUALITY_COL, self.UPDATE_TIMESTAMP_COL}
        columns = set(self._df.columns)
        if required_columns - columns:
            raise TimeseriesMissingColumnError(
                'Missing {} columns in input dataframe'
                .format(required_columns - columns))
        if columns - allowed_columns:
            raise TimeseriesInvalidColumnsError(
                'Invalid columns in data: {}'
                .format(columns - allowed_columns))

        # Set default quality and update_ts if needed
        if self.QUALITY_COL not in self._df:
            self._df[self.QUALITY_COL] = 1
        if self.UPDATE_TIMESTAMP_COL not in self._df:
            self._df[self.UPDATE_TIMESTAMP_COL] = pd.NaT

        # Enforce dtype on value and quality
        for col in (self.DATA_COL, self.QUALITY_COL):
            if self._df[col].dtype is not np.dtype('float64'):
                self._df[col] = self._df[col].astype('float64')

        # Enforce index name
        if self._df.index.name != self.TIMESTAMPS_COL:
            self._df.index.name = self.TIMESTAMPS_COL

    def set_update_timestamp(self, dtime):
        """Set update timestamp (update_ts) for all values.

        :param datetime|list|pandas.Series dtime: New update time stamp.
        """
        self.dataframe[self.UPDATE_TIMESTAMP_COL] = dtime

    def stats(self):
        # TODO: modify TimeseriesMgr to avoid fetching all the data?
        if self.dataframe.empty:
            return {'count': len(self.dataframe)}
        return {
            'count': len(self.dataframe),
            'start': self.dataframe.index.min(),
            'end': self.dataframe.index.max(),
            'update_ts': self.dataframe[self.UPDATE_TIMESTAMP_COL].max()
        }

    def convert_unit(self, source_unit, target_unit, *, decimals=2):
        """Convert the data of timeseries (DATA_COL) from an unit to another
        compatible unit. Operation is "in-place", so data values are replaced.

        :param str source_unit: Unit symbol to convert from.
        :param str target_unit: Unit symbol to convert to.
        :param int decimals: (optional, default 2)
            Number of decimal places to round to. If decimals is negative, it
            specifies the number of positions to the left of the decimal point.
        :raises TimeseriesUnitConversionError:
            When a target unit is not defined (None).
            When a source/target unit is unknown.
            When a source and target units are not compatible.
        """
        if source_unit is None:
            raise TimeseriesUnitConversionError('Source unit must be defined.')
        if target_unit is None:
            raise TimeseriesUnitConversionError('Target unit must be defined.')

        # get bemserver units equivalency in Pint units
        pint_source_unit = units.get_pint_unit(source_unit)
        pint_target_unit = units.get_pint_unit(target_unit)
        if pint_source_unit is None:
            raise TimeseriesUnitConversionError('Source unit is unknown.')
        if pint_target_unit is None:
            raise TimeseriesUnitConversionError('Target unit is unknown.')

        src_data = self._df[self.DATA_COL].values
        try:
            q_src_data = units.ureg.Quantity(src_data, pint_source_unit)
        except units.errors.UndefinedUnitError as exc:
            raise TimeseriesUnitConversionError(str(exc))
        try:
            # convert data and round result
            self._df[self.DATA_COL] = np.around(
                q_src_data.to(pint_target_unit), decimals)
        except (units.errors.DimensionalityError,
                units.errors.UndefinedUnitError) as exc:
            raise TimeseriesUnitConversionError(str(exc))

    def resample(self, freq, operation):
        """Resample DataFrame

        Resample DataFrame to provided freq, using provided operation to
        aggregate data column.

        Quality and update timestamp columns are aggregated using mean and max
        respectively.

        :param str freq: New sampling frequency.
            Must be in AGG_FREQUENCIES.keys().
        :param str operation: Aggregation operation to apply to data.
            Muse be in AGG_OPERATIONS
        """
        # Things were almost perfect, until sum([np.NaN]) decided to return 0
        # https://pandas.pydata.org/pandas-docs/version/0.22.0/whatsnew.html
        #     #backwards-incompatible-api-changes
        if operation == 'sum':
            operation = lambda x: x.sum(min_count=1)
        self._df = self._df.resample(self.AGG_FREQUENCIES[freq]).agg({
            self.DATA_COL: operation,
            self.QUALITY_COL: 'mean',
            self.UPDATE_TIMESTAMP_COL: 'max',
        }).dropna(subset=['data'])
