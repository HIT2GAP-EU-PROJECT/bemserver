"""Tests on database timeseries manager"""

import datetime as dt
import pytz
import numpy as np
import pandas as pd
import pytest

from bemserver.models import Timeseries
from bemserver.database.timeseries.hdfstore import (
    HDFStoreTimeseriesMgr, HDF_LOCK)

from tests import TestCoreDatabase


class TestHDFStoreTimeseriesManager(TestCoreDatabase):
    """Tests for HDFStore timeseries manager"""

    def test_hdfstore_timeseries_manager(self, tmpdir):

        t_before_start_1 = dt.datetime(2016, 12, 1)
        t_before_start_2 = dt.datetime(2016, 12, 2)
        t_start = dt.datetime(2017, 1, 1)
        t_inside_1 = dt.datetime(2017, 1, 1, 8, 12, 42)
        t_inside_2 = dt.datetime(2017, 1, 1, 16, 42, 12)
        t_end = dt.datetime(2017, 1, 2)
        t_after_end_1 = dt.datetime(2017, 2, 1)
        t_after_end_2 = dt.datetime(2017, 2, 2)
        index = pd.date_range(t_start, t_end, freq='min', closed='left')

        mgr = HDFStoreTimeseriesMgr(str(tmpdir))

        # Get unknown timestore ID
        df = mgr.get('test', 'dummy', t_start=t_start, t_end=t_end).dataframe
        assert df.empty

        # Set unexisting ID: no problem
        ts = Timeseries(
            index=index, data=np.random.rand(len(index)),
            quality=np.random.rand(len(index)), update_ts=index)
        mgr.set('test', '/df', ts)
        df = ts.dataframe

        # Query new dataframe
        new_df = mgr.get('test', '/df', t_start=t_start, t_end=t_end).dataframe
        assert new_df['data'].equals(df['data'])
        assert new_df.index.equals(df.index)

        # Query new dataframe out of bounds
        new_df = mgr.get(
            'test', '/df', t_start=t_before_start_1, t_end=t_before_start_2
        ).dataframe
        assert new_df.empty
        new_df = mgr.get(
            'test', '/df', t_start=t_after_end_1, t_end=t_after_end_2
        ).dataframe
        assert new_df.empty

        # Query sub-timerange
        new_df = mgr.get(
            'test', '/df', t_start=t_inside_1, t_end=t_inside_2
        ).dataframe
        assert len(new_df) == 510

        # Query straddling a bound
        new_df = mgr.get(
            'test', '/df', t_start=t_before_start_2, t_end=t_inside_1
        ).dataframe
        assert len(new_df) == 493

        # Override some values
        ts = Timeseries(
            index=index[:5], data=np.arange(5, dtype='float'),
            quality=np.random.rand(5), update_ts=index[:5])
        mgr.set('test', '/df', ts)
        new_df = mgr.get('test', '/df', t_start=t_start, t_end=t_end).dataframe
        assert len(new_df) == 1440
        new_df = mgr.get(
            'test', '/df', t_start=index[0], t_end=index[5]).dataframe
        assert new_df['data'].tolist() == [float(x) for x in range(5)]

        # Delete values
        mgr.delete('test', '/df', index[5], index[10])
        new_df = mgr.get('test', '/df', t_start=t_start, t_end=t_end).dataframe
        assert len(new_df) == 1435
        new_df = mgr.get(
            'test', '/df', t_start=index[0], t_end=index[10]).dataframe
        assert new_df['data'].tolist() == [float(x) for x in range(5)]

    def test_hdfstore_timeseries_manager_persistance(self, tmpdir):
        """Ensure data is persistance accross manager instances"""

        t_start = dt.datetime(2017, 1, 1)
        t_end = dt.datetime(2017, 1, 2)
        index = pd.date_range(t_start, t_end, freq='min', closed='left')

        ts = Timeseries(
            index=index, data=np.random.rand(len(index)),
            quality=np.random.rand(len(index)), update_ts=index)

        mgr = HDFStoreTimeseriesMgr(str(tmpdir))
        # Store new dataframe
        mgr.set('test', '/df', ts)
        df = mgr.get('test', '/df', t_start=t_start, t_end=t_end).dataframe
        assert len(df) == 60 * 24
        del mgr

        mgr = HDFStoreTimeseriesMgr(str(tmpdir))
        df = mgr.get('test', '/df', t_start=t_start, t_end=t_end).dataframe
        assert len(df) == 60 * 24

    def test_hdfstore_timeseries_manager_get_bounds(self, tmpdir):
        """Test get optional time bounds"""
        t_start = dt.datetime(2017, 1, 1)
        t_end = dt.datetime(2017, 1, 2)
        index = pd.date_range(t_start, t_end, freq='min', closed='left')

        mgr = HDFStoreTimeseriesMgr(str(tmpdir))
        ts = Timeseries(index=index, data=np.random.rand(len(index)))
        mgr.set('test', '/df', ts)
        df = ts.dataframe

        new_df = mgr.get('test', '/df', t_start=t_start, t_end=t_end).dataframe
        assert new_df['data'].equals(df['data'])
        assert new_df.index.equals(df.index)

        new_df = mgr.get('test', '/df').dataframe
        assert new_df['data'].equals(df['data'])
        assert new_df.index.equals(df.index)

        new_df = mgr.get('test', '/df', t_start=t_start).dataframe
        assert new_df['data'].equals(df['data'])
        assert new_df.index.equals(df.index)

        new_df = mgr.get('test', '/df', t_end=t_end).dataframe
        assert new_df['data'].equals(df['data'])
        assert new_df.index.equals(df.index)

    def test_hdfstore_timeseries_manager_datetime_awareness(self, tmpdir):
        """Check behavior with regard to datetime awareness"""

        # To test for awareness, see https://stackoverflow.com/a/27596917

        def isaware(ts):
            return (
                ts.tzinfo is not None and ts.tzinfo.utcoffset(ts) is not None)

        def isnaive(ts):
            return ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None

        t1_n = dt.datetime(2017, 1, 1)
        t2_n = dt.datetime(2017, 1, 2)
        t2_a = dt.datetime(2017, 1, 2).replace(tzinfo=pytz.UTC)
        t3_a = dt.datetime(2017, 1, 3).replace(tzinfo=pytz.UTC)
        index_n = pd.date_range(t1_n, t2_n, freq='min', closed='left')
        index_a = pd.date_range(t2_a, t3_a, freq='min', closed='left')

        ts_n = Timeseries(
            index=index_n, data=np.random.rand(len(index_n)),
            update_ts=index_n)
        ts_a = Timeseries(
            index=index_a, data=np.random.rand(len(index_a)),
            update_ts=index_a)

        mgr = HDFStoreTimeseriesMgr(str(tmpdir))

        # Naive index dataframe
        mgr.set('test', '/df_n', ts_n)
        df = mgr.get('test', '/df_n', t_start=t1_n, t_end=t2_n).dataframe
        ts_0 = df.index[0]
        assert isnaive(ts_0)

        # Aware index dataframe (TZ = UTC)
        mgr.set('test', '/df_a', ts_a)
        df = mgr.get('test', '/df_a', t_start=t2_a, t_end=t3_a).dataframe
        ts_0 = df.index[0]
        assert isaware(ts_0)

        # Mix both -> every index is considered UTC
        mgr.set('test', '/df_m', ts_n)
        mgr.set('test', '/df_m', ts_a)
        df = mgr.get('test', '/df_m', t_start=t1_n, t_end=t3_a).dataframe
        ts_0 = df.index[0]
        ts_1 = df.index[-1]
        assert isaware(ts_0)
        assert isaware(ts_1)

    def test_hdfstore_timeseries_manager_sorted(self, tmpdir):
        """Check hdfstore returns a sorted index dataframe"""
        t_start1 = dt.datetime(2017, 1, 1)
        t_end1 = dt.datetime(2017, 1, 6)
        index1 = pd.date_range(t_start1, t_end1, freq='D', closed='left')
        t_start2 = dt.datetime(2017, 1, 3)
        t_end2 = dt.datetime(2017, 1, 5)
        index2 = pd.date_range(t_start2, t_end2, freq='D', closed='left')
        df1 = pd.DataFrame({'data': range(len(index1))}, index=index1)
        df2 = pd.DataFrame({'data': range(len(index2))}, index=index2)

        mgr = HDFStoreTimeseriesMgr(str(tmpdir))
        mgr.set('test', 'df', Timeseries.from_dataframe(df1))
        mgr.set('test', 'df', Timeseries.from_dataframe(df2))
        ts_out = mgr.get('test', 'df', t_start=t_start1, t_end=t_end1)
        assert ts_out.dataframe.index.equals(index1)

    def test_hdfstore_timeseries_manager_exception(self, tmpdir):
        """Check hdfstore exceptions are not ignored"""
        mgr = HDFStoreTimeseriesMgr(str(tmpdir))
        with pytest.raises(AttributeError):
            mgr.set('test', 'df', 'dummy Timeseries')
        # Check lock was released
        assert not HDF_LOCK.locked()

    def test_hdfstore_timeseries_manager_quality_defaults_to_1(self, tmpdir):
        """Check quality read as NaN in DB is changed into 1

        This is a patch for data registered before the default was introduced.
        """
        t_start = dt.datetime(2017, 1, 1)
        t_end = dt.datetime(2017, 1, 2)
        index = pd.date_range(t_start, t_end, freq='H', closed='left')
        data = np.random.rand(len(index))
        quality = np.random.rand(len(index))
        mgr = HDFStoreTimeseriesMgr(str(tmpdir))

        # Test with real values and NaN
        quality[::2] = [np.NaN] * len(quality[::2])
        ts = Timeseries(
            index=index, data=data, quality=quality, update_ts=index)
        mgr.set('test', '/df', ts)
        df = mgr.get('test', '/df').dataframe
        assert (df.quality[::2] == 1).all()

        # Test with only NaN
        quality = [np.NaN] * len(quality)
        ts = Timeseries(
            index=index, data=data, quality=quality, update_ts=index)
        mgr.set('test', '/df', ts)
        df = mgr.get('test', '/df').dataframe
        assert (df.quality == 1).all()
