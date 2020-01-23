"""Tests for Timeseries object"""

from copy import deepcopy
import datetime as dt
from math import isclose
import numpy as np
import pandas as pd
import pytest
from bemserver.models import Timeseries
from bemserver.models.timeseries.exceptions import (
    TimeseriesInvalidIndexTypeError,
    TimeseriesMissingColumnError, TimeseriesInvalidColumnsError,
    TimeseriesUnitConversionError)

from tests import TestCoreModel
from tests.utils import celsius_to_fahrenheit


class TestTimeseries(TestCoreModel):

    def test_timeseries_columns(self):

        assert Timeseries.TIMESTAMPS_COL == 'index'
        assert Timeseries.DATA_COL == 'data'
        assert Timeseries.QUALITY_COL == 'quality'
        assert Timeseries.UPDATE_TIMESTAMP_COL == 'update_ts'

    def test_timeseries_init_empty_dataframe(self):

        ts = Timeseries()
        assert isinstance(ts.dataframe, pd.DataFrame)
        assert not len(ts.dataframe)
        assert ts.dataframe.index.name == 'index'

        assert set(
            zip(
                ts.dataframe.columns.tolist(),
                ts.dataframe.dtypes.tolist(),
            )
        ) == {
            ('quality', np.dtype('float64')),
            ('update_ts', np.dtype('<M8[ns]')),
            ('data', np.dtype('float64')),
        }

        assert repr(ts) == (
            '<Timeseries>(count=0, start=NaT, end=NaT, min=nan, max=nan)')

    def test_timeseries_init_dataframe(self):

        t_start = dt.datetime(2017, 1, 1)
        t_end = dt.datetime(2017, 1, 6)
        index = pd.date_range(t_start, t_end, freq='D', closed='left')

        # index column must be a pandas.DatetimeIndex
        with pytest.raises(TimeseriesInvalidIndexTypeError):
            Timeseries(index=range(5), data=range(5))
        # quality can not be set without data
        with pytest.raises(TimeseriesMissingColumnError):
            Timeseries(index=index, quality=np.random.rand(len(index)))
        # data can not be set without index
        with pytest.raises(TimeseriesMissingColumnError):
            Timeseries(data=range(len(index)))

        # validate dataframe
        ts = Timeseries(index=index, data=range(len(index)))
        # no custom column allowed
        ts.dataframe['dummy'] = range(len(index))
        with pytest.raises(TimeseriesInvalidColumnsError):
            ts.validate()
        # droping a column unvalidates timeseries
        ts.dataframe.drop(columns=['dummy', 'data'], inplace=True)
        with pytest.raises(TimeseriesMissingColumnError):
            ts.validate()

        # repr timeseries
        ts_data = range(len(index))
        ts = Timeseries(index=index, data=ts_data)
        assert repr(ts) == (
            '<Timeseries>(count={}, start={}, end={}, min={}, max={})'.format(
                len(index), min(index), max(index),
                float(min(ts_data)), float(max(ts_data))))

        # quality defaults to 1
        ts = Timeseries(index=index, data=range(len(index)))
        assert (ts.dataframe['quality'] == 1).all()

        # update_ts can only be set using set_update_timestamp method
        ts = Timeseries(
            index=index, data=range(len(index)),
            quality=np.random.rand(len(index)))
        assert pd.isnull(ts.dataframe['update_ts']).all()
        # update with a pandas.Series
        ts.set_update_timestamp(index)
        assert ts.dataframe.at[index[0], 'update_ts'] == index.values[0]
        # update with a datetime
        t_update = dt.datetime.now()
        ts.set_update_timestamp(t_update)
        assert ts.dataframe.at[index[0], 'update_ts'] == t_update
        ts.validate()
        assert ts.dataframe.at[index[0], 'update_ts'] == t_update
        # update with a list of datetimes
        t_update = [dt.datetime.now()] * len(index)
        ts.set_update_timestamp(t_update)
        assert ts.dataframe.at[index[0], 'update_ts'] == t_update[0]
        ts.validate()
        assert ts.dataframe.at[index[0], 'update_ts'] == t_update[0]

        # data length must be equal to index length
        with pytest.raises(ValueError):
            Timeseries(index=index, data=range(len(index)+1))

    def test_timeseries_stats(self):
        index = [
            dt.datetime(2017, 1, 5),
            dt.datetime(2017, 1, 1),
            dt.datetime(2017, 1, 8),
            dt.datetime(2017, 1, 3),
        ]
        data = [1, 2, 3, 4]
        df = pd.DataFrame({'data': data}, index=index)
        ts = Timeseries.from_dataframe(df)
        assert ts.stats() == {
            'count': 4,
            'start': dt.datetime(2017, 1, 1),
            'end': dt.datetime(2017, 1, 8),
            'update_ts': ts.dataframe[Timeseries.UPDATE_TIMESTAMP_COL].max()
        }

    def test_timeseries_convert(self):

        t_start = dt.datetime(2017, 1, 1)
        t_end = dt.datetime(2017, 1, 6)
        index = pd.date_range(t_start, t_end, freq='D', closed='left')
        data = range(len(index))
        ts = Timeseries(index=index, data=data)

        # convert from celsius to fahreinheit
        ts.convert_unit('DegreeCelsius', 'DegreeFahrenheit')
        for idx, cur_val in enumerate(ts.dataframe[ts.DATA_COL].values):
            # as values are rounded, check strict equality
            assert cur_val == celsius_to_fahrenheit(data[idx])

        # convert from celsius to fahreinheit, rounding to 4 decimals
        ts = Timeseries(index=index, data=data)
        ts.convert_unit('DegreeCelsius', 'DegreeFahrenheit', decimals=4)
        for idx, cur_val in enumerate(ts.dataframe[ts.DATA_COL].values):
            # as values are rounded, check strict equality
            assert cur_val == celsius_to_fahrenheit(data[idx], decimals=4)

        # convert from MWh to kWh
        ts.convert_unit('Megawatthour', 'Kilowatthour')
        # convert using square meters
        ts.convert_unit('WattSquareMeter', 'KilowattSquareMeter')

        # source and target units are not compatible
        with pytest.raises(TimeseriesUnitConversionError):
            ts.convert_unit('DegreeCelsius', 'Meter')

        # unknown source or target unit
        with pytest.raises(TimeseriesUnitConversionError):
            ts.convert_unit('inexistant', 'DegreeFahrenheit')
        with pytest.raises(TimeseriesUnitConversionError):
            ts.convert_unit('DegreeCelsius', 'inexistant')
        with pytest.raises(TimeseriesUnitConversionError):
            ts.convert_unit(None, 'DegreeFahrenheit')
        with pytest.raises(TimeseriesUnitConversionError):
            ts.convert_unit('DegreeCelsius', None)

        # Test custom units
        ts = Timeseries(index=index, data=data)
        ts.convert_unit('Percent', 'Permille')
        assert all(
            new == round(10 * old, 2)
            for (old, new) in zip(data, ts.dataframe[ts.DATA_COL].values))
        ts.convert_unit('Permille', 'PartsPerMillion')
        assert all(
            new == round(10000 * old, 2)
            for (old, new) in zip(data, ts.dataframe[ts.DATA_COL].values))
        ts.convert_unit('PartsPerMillion', 'Unitless')
        assert all(
            new == round(0.01 * old, 2)
            for (old, new) in zip(data, ts.dataframe[ts.DATA_COL].values))

    def test_timeseries_resample(self):
        t_start = dt.datetime(2017, 1, 1)
        t_end = dt.datetime(2018, 1, 1)
        index = pd.date_range(t_start, t_end, freq='T', closed='left')
        data = range(len(index))
        quality = [i % 2 for i in range(len(index))]
        ts0 = Timeseries(index=index, data=data, quality=quality)
        ts0.set_update_timestamp(index)

        ts1 = deepcopy(ts0)
        ts1.resample('month', 'first')
        assert len(ts1.dataframe) == 12
        assert isclose(ts1.dataframe.data[0], 0)
        assert isclose(ts1.dataframe.data[1], 44640)
        assert isclose(ts1.dataframe.data[-1], 480960)
        assert np.all(np.isclose(ts1.dataframe.quality, 0.5))

        ts2 = deepcopy(ts0)
        ts2.resample('day', 'max')
        assert len(ts2.dataframe) == 365
        assert isclose(ts2.dataframe.data[0], 1439)
        assert isclose(ts2.dataframe.data[1], 2879)
        assert isclose(ts2.dataframe.data[-1], 525599)

        ts3 = deepcopy(ts0)
        ts3.resample('30min', 'sum')
        assert len(ts3.dataframe) == len(index) / 30
        for i in range(len(ts3.dataframe)):
            assert isclose(
                ts3.dataframe.data[i], sum(range(30 * i, 30 * (i + 1))))

    @pytest.mark.parametrize('operation', Timeseries.AGG_OPERATIONS)
    def test_timeseries_resample_no_upsample(self, operation):
        """Check resample does not upsample"""
        t_start = dt.datetime(2017, 1, 1)
        t_end = dt.datetime(2017, 1, 1, 0, 10)
        index = pd.date_range(t_start, t_end, freq='T', closed='left')
        data = range(len(index))
        ts0 = Timeseries(index=index, data=data)
        ts1 = deepcopy(ts0)
        ts1.resample('sec', operation)

    def test_timeseries_aggregate(self):
        """Check aggregate function"""
        def generate_ts(number, random=False, nan=False):
            for _ in range(number):
                # Generate index
                t_start = dt.datetime(2017, 1, 1)
                t_end = dt.datetime(2018, 1, 1)
                index = pd.date_range(t_start, t_end, freq='D', closed='left')
                if nan:
                    mask = np.random.choice([True, False], len(index))
                    index = index[mask]
                # Generate data
                if random:
                    data = 100 * np.random.rand(len(index))
                    quality = np.random.randint(2, size=len(index))
                else:
                    data = range(len(index))
                    quality = [i % 2 for i in range(len(index))]
                yield Timeseries(index=index, data=data, quality=quality)

        number = 5

        # Test with fixed data, with same length and same values
        list1 = list(generate_ts(number))
        ts_len = len(list1[0].dataframe)
        aggregation = Timeseries.aggregate(list1, 'sum')
        assert isinstance(aggregation, Timeseries)
        assert len(aggregation.dataframe) == ts_len
        sample = aggregation.dataframe.sample(n=100)
        for index in sample.index.values:
            data_sum = sum([ts.dataframe.data[index] for ts in list1])
            quality_mean = sum(
                [ts.dataframe.quality[index] for ts in list1]) / number
            assert isclose(sample.data[index], data_sum)
            assert isclose(sample.quality[index], quality_mean)

        # Test with random data
        list2 = list(generate_ts(number, random=True, nan=True))
        aggregation = Timeseries.aggregate(list2, 'max')
        assert isinstance(aggregation, Timeseries)
        sample = aggregation.dataframe.sample(n=100)
        for index in sample.index.values:
            data_max = max([
                ts.dataframe.data[index]
                for ts in list2
                if index in ts.dataframe.data.index])
            quality_mean = sum([
                ts.dataframe.quality[index] for ts in list2
                if index in ts.dataframe.quality.index]) / number
            assert isclose(sample.data[index], data_max)
            assert isclose(sample.quality[index], quality_mean)
            assert 0 <= sample.data[index] <= 100
            assert 0 <= sample.quality[index] <= 1
