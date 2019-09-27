"""Tests for api measure views"""

import datetime as dt
import random
import statistics
from math import isclose
from dateutil.tz import tzutc
import flask
import numpy as np
import pandas as pd
import pytest

from bemserver.models import Timeseries
from bemserver.api.views.timeseries.tsio import (
    get_timeseries_manager, tsload, tsdump)
from bemserver.api.views.timeseries.exceptions import (
    TimeseriesConfigError)

from tests import TestCore, TestCoreApi
from tests.utils import celsius_to_fahrenheit


class TestApiTimeseries(TestCore):
    """Tests not specific to any database implementation"""

    def test_get_timeries_manager(self, tmpdir):

        class InvalidBackendConfig():
            TIMESERIES_BACKEND = 'dummy'

        class MissingStorageDirHDFStoreConfig():
            TIMESERIES_BACKEND = 'hdfstore'

        for config_cls in [
                InvalidBackendConfig,
                MissingStorageDirHDFStoreConfig,
        ]:
            app = flask.Flask('Test')
            app.config.from_object(config_cls)
            with app.app_context():
                with pytest.raises(TimeseriesConfigError):
                    get_timeseries_manager()

        class CorrectHDFStoreConfig():
            TIMESERIES_BACKEND = 'hdfstore'
            TIMESERIES_BACKEND_STORAGE_DIR = str(tmpdir)

        for config_cls in [
                CorrectHDFStoreConfig
        ]:
            app = flask.Flask('Test')
            app.config.from_object(config_cls)
            with app.app_context():
                get_timeseries_manager()

    def test_timeseries_tsload(self):
        timestamp_l = [
            dt.datetime(2017, 1, 1) + dt.timedelta(n) for n in range(5)]
        value_l = [0, 1, 2, 3, 4]
        quality_l = [1, 1, 0.5, None, 0.69]
        update_ts_l = [dt.datetime.now()] * 5

        data_list = []
        ts_df = tsload(data_list).dataframe
        assert isinstance(ts_df, pd.DataFrame)
        assert len(ts_df) == 0
        assert ts_df.index.name == 'index'
        assert set(ts_df.columns.tolist()) == {'data', 'quality', 'update_ts'}
        assert ts_df.equals(Timeseries.empty_dataframe())

        data_list = [
            {'timestamp': t, 'value': v}
            for t, v in zip(timestamp_l, value_l)
        ]
        ts_df = tsload(data_list).dataframe
        assert isinstance(ts_df, pd.DataFrame)
        assert ts_df.index.tolist() == timestamp_l
        assert ts_df[Timeseries.DATA_COL].tolist() == value_l
        assert set(ts_df.columns.tolist()) == {
            Timeseries.DATA_COL, Timeseries.QUALITY_COL,
            Timeseries.UPDATE_TIMESTAMP_COL}
        assert ts_df[Timeseries.DATA_COL].dtype == np.dtype('float')

        data_list = [
            {'timestamp': t, 'value': v, 'quality': q}
            for t, v, q in zip(timestamp_l, value_l, quality_l)
        ]
        ts_df = tsload(data_list).dataframe
        assert isinstance(ts_df, pd.DataFrame)
        assert ts_df.index.tolist() == timestamp_l
        assert ts_df[Timeseries.DATA_COL].tolist() == value_l
        qual_s = ts_df[Timeseries.QUALITY_COL]
        assert qual_s.where(pd.notnull(qual_s), None).tolist() == quality_l
        assert set(ts_df.columns.tolist()) == {
            Timeseries.DATA_COL, Timeseries.QUALITY_COL,
            Timeseries.UPDATE_TIMESTAMP_COL}
        assert ts_df[Timeseries.DATA_COL].dtype == np.dtype('float')
        assert ts_df[Timeseries.QUALITY_COL].dtype == np.dtype('float')

        data_list = [
            {'timestamp': t, 'value': v, 'quality': q, 'update_ts': u}
            for t, v, q, u in zip(timestamp_l, value_l, quality_l, update_ts_l)
        ]
        ts_df = tsload(data_list).dataframe
        assert isinstance(ts_df, pd.DataFrame)
        assert ts_df.index.tolist() == timestamp_l
        assert ts_df[Timeseries.DATA_COL].tolist() == value_l
        qual_s = ts_df[Timeseries.QUALITY_COL]
        assert qual_s.where(pd.notnull(qual_s), None).tolist() == quality_l
        assert (
            ts_df[Timeseries.UPDATE_TIMESTAMP_COL].tolist() == update_ts_l)
        assert set(ts_df.columns.tolist()) == {
            Timeseries.DATA_COL, Timeseries.QUALITY_COL,
            Timeseries.UPDATE_TIMESTAMP_COL}
        assert ts_df[Timeseries.DATA_COL].dtype == np.dtype('float')
        assert ts_df[Timeseries.QUALITY_COL].dtype == np.dtype('float')
        assert (ts_df[Timeseries.UPDATE_TIMESTAMP_COL].dtype ==
                np.dtype('datetime64[ns]'))

    def test_timeseries_tsdump(self):
        timestamp_l = [
            dt.datetime(2017, 1, 1) + dt.timedelta(n) for n in range(5)]
        value_l = [0, 1, 2, 3, 4]
        quality_l = [1, 1, 0.5, None, 0.69]
        update_ts_l = [dt.datetime.now()] * 5

        ts = Timeseries(index=timestamp_l, data=value_l, quality=quality_l)
        ts.set_update_timestamp(update_ts_l)
        assert np.isnan(ts.dataframe['quality'][3])

        ts_list = tsdump(ts)
        assert len(ts_list) == 5
        assert all(len(v) == 4 for v in ts_list)
        assert [v['timestamp'] for v in ts_list] == timestamp_l
        assert [v['value'] for v in ts_list] == value_l
        assert [v['update_ts'] for v in ts_list] == update_ts_l
        assert [v['quality'] for v in ts_list] == quality_l


@pytest.mark.usefixtures('init_app')
class TestApiViewsTimeseries(TestCoreApi):
    """Measure api views tests"""

    base_uri = '/timeseries/'

    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_timeseries_api(self, init_db_data):
        """Check timeseries view"""

        db_data = init_db_data
        measure_id = str(db_data['measures'][0])

        response = self.get_item_by_id(uri='/measures/', item_id=measure_id)
        assert response.status_code == 200
        ts_metadata = response.json
        ts_id = ts_metadata['external_id']

        t_start = dt.datetime(2017, 1, 1).isoformat()
        t_end = dt.datetime(2017, 6, 1).isoformat()
        # Note: we add TZ info here for later comparison with API output:
        # timestamps are serialized as TZ aware UTC
        timestamp_l = [
            (dt.datetime(2017, 1, 1, tzinfo=tzutc()) +
             dt.timedelta(n)).isoformat()
            for n in range(5)]
        value_l = [0, 1, 2, 3, 4]
        quality_l = [0.5, 0.5, 0.8, 1, 0.69]

        data_list_v = [
            {'timestamp': t, 'value': v}
            for t, v in zip(timestamp_l, value_l)
        ]
        data_list_v_q = [
            {'timestamp': t, 'value': v, 'quality': q}
            for t, v, q in zip(timestamp_l, value_l, quality_l)
        ]
        # Test quality is not required
        del data_list_v_q[3]['quality']

        # Get data from non existing timeseries -> 404
        response = self.get_item_by_id(
            item_id='dummy', start_time=t_start, end_time=t_end)
        assert response.status_code == 404

        # Get data from empty timeseries -> 200
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end)
        assert response.status_code == 200
        assert response.json['data'] == []

        # Set data
        response = self.patch_item(ts_id, data=data_list_v)
        assert response.status_code == 204

        # Get data
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end)
        assert response.status_code == 200
        ts_list = response.json['data']
        assert len(ts_list) == 5
        assert all(len(v) == 4 for v in ts_list)
        assert [v['timestamp'] for v in ts_list] == timestamp_l
        assert [v['value'] for v in ts_list] == value_l

        # Unit conversion
        # Get data, converting unit
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end,
            unit='DegreeFahrenheit')
        assert response.status_code == 200
        ts_list = response.json['data']
        for idx, row in enumerate(ts_list):
            expected_value = celsius_to_fahrenheit(value_l[idx])
            assert row['value'] == expected_value
        # Get data, converting to a not compatible unit
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end, unit='meter')
        assert response.status_code == 422
        # Get data, converting to an unknown unit
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end, unit='zblorg')
        assert response.status_code == 422

        # Set data with quality
        response = self.patch_item(ts_id, data=data_list_v_q)
        assert response.status_code == 204

        # Get data with quality
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end)
        assert response.status_code == 200
        ts_list = response.json['data']
        assert len(ts_list) == 5
        assert all(len(v) == 4 for v in ts_list)
        assert [v['timestamp'] for v in ts_list] == timestamp_l
        assert [v['value'] for v in ts_list] == value_l
        assert all('update_ts' in v for v in ts_list)

        # Set data, converting unit from fahrenheit to celsius
        data_list = [
            {'timestamp': t, 'value': celsius_to_fahrenheit(v), 'quality': q}
            for t, v, q in zip(timestamp_l, value_l, quality_l)
        ]
        response = self.patch_item(
            ts_id, data=data_list, unit='DegreeFahrenheit')
        assert response.status_code == 204
        # Get data to check unit conversion while pathcing
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end)
        assert response.status_code == 200
        ts_list = response.json['data']
        for idx, row in enumerate(ts_list):
            assert celsius_to_fahrenheit(
                row['value']) == data_list[idx]['value']
        # Set data, converting unit, source unit unknown!
        response = self.patch_item(ts_id, data=data_list, unit='zblorg')
        assert response.status_code == 422

        # Ensure we don't crash on empty data
        response = self.patch_item(ts_id, data=[])
        assert response.status_code == 204

        # Delete part of the data
        response = self.delete_item(
            item_id=ts_id, start_time=timestamp_l[0], end_time=timestamp_l[2])
        assert response.status_code == 204

        # Get data and check it was partially deleted
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end)
        assert response.status_code == 200
        ts_list = response.json['data']
        assert len(ts_list) == 3
        assert all(len(v) == 4 for v in ts_list)
        assert [v['timestamp'] for v in ts_list] == timestamp_l[2:]
        assert [v['value'] for v in ts_list] == value_l[2:]
        assert all('update_ts' in v for v in ts_list)

    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_timeseries_resample(self, init_db_data):
        """Check timeseries resample view"""

        db_data = init_db_data
        measure_id = str(db_data['measures'][0])

        response = self.get_item_by_id(uri='/measures/', item_id=measure_id)
        assert response.status_code == 200
        ts_metadata = response.json
        ts_id = ts_metadata['external_id']

        # Note: we add TZ info here for later comparison with API output:
        # timestamps are serialized as TZ aware UTC
        t_start_dt = dt.datetime(2017, 1, 1, tzinfo=tzutc())
        t_end_dt = dt.datetime(2017, 3, 1, tzinfo=tzutc())
        t_m1_dt = dt.datetime(2017, 2, 1, tzinfo=tzutc())
        t_h1_dt = dt.datetime(2017, 1, 1, 1, tzinfo=tzutc())
        t_30min1_dt = dt.datetime(2017, 1, 1, 0, 30, tzinfo=tzutc())
        t_h3_dt = dt.datetime(2017, 1, 1, 3, tzinfo=tzutc())
        nb_30_mins = int((t_end_dt - t_start_dt).total_seconds() / 1800)
        t_start = t_start_dt.isoformat()
        t_end = t_end_dt.isoformat()
        timestamp_l = [
            (dt.datetime(2017, 1, 1, tzinfo=tzutc()) +
             dt.timedelta(seconds=1800 * n)).isoformat()
            for n in range(nb_30_mins)]
        value_l = range(nb_30_mins)
        quality_l = [i % 2 for i in range(nb_30_mins)]
        nb_samples_m1 = int((t_m1_dt - t_start_dt).total_seconds() / 1800)
        nb_samples_h1 = int((t_h1_dt - t_start_dt).total_seconds() / 1800)

        data_list = [
            {'timestamp': t, 'value': v, 'quality': q}
            for t, v, q in zip(timestamp_l, value_l, quality_l)
        ]

        # Set data
        response = self.patch_item(ts_id, data=data_list)
        assert response.status_code == 204

        # Get resampled data: monthly sum
        response = self.client.get(
            '/timeseries/{}/resample'.format(ts_id),
            query_string={
                'freq': 'month', 'aggregation': 'sum',
                'start_time': t_start, 'end_time': t_end, })
        resp_data = response.json['data']
        assert resp_data[0]['timestamp'] == t_start
        assert resp_data[1]['timestamp'] == t_m1_dt.isoformat()
        assert isclose(resp_data[0]['value'], 1106328)
        assert isclose(resp_data[1]['value'], 2902368)
        assert isclose(resp_data[0]['quality'], statistics.mean(
            quality_l[:nb_samples_m1]))
        assert isclose(resp_data[1]['quality'], statistics.mean(
            quality_l[nb_samples_m1:]))

        # Get resampled data: hourly max
        response = self.client.get(
            '/timeseries/{}/resample'.format(ts_id),
            query_string={
                'freq': 'hour', 'aggregation': 'max',
                'start_time': t_start, 'end_time': t_h3_dt.isoformat(), })
        resp_data = response.json['data']
        assert len(resp_data) == 3
        assert resp_data[0]['timestamp'] == t_start
        assert resp_data[1]['timestamp'] == t_h1_dt.isoformat()
        assert isclose(resp_data[0]['value'], 1)
        assert isclose(resp_data[1]['value'], 3)
        assert isclose(resp_data[2]['value'], 5)
        assert isclose(resp_data[0]['quality'], statistics.mean(
            quality_l[:nb_samples_h1]))

        # Get resampled data: minute mean
        # Check resample does not do upsampling or fill any gap
        response = self.client.get(
            '/timeseries/{}/resample'.format(ts_id),
            query_string={
                'freq': 'min', 'aggregation': 'mean',
                'start_time': t_start, 'end_time': t_h1_dt.isoformat(), })
        resp_data = response.json['data']
        assert len(resp_data) == 2
        assert resp_data[0]['timestamp'] == t_start
        assert resp_data[1]['timestamp'] == t_30min1_dt.isoformat()
        assert isclose(resp_data[0]['value'], 0)
        assert isclose(resp_data[1]['value'], 1)
        assert isclose(resp_data[0]['quality'], 0)
        assert isclose(resp_data[1]['quality'], 1)

        # Unit conversion
        # Get resampled data, converting unit
        response = self.client.get(
            '/timeseries/{}/resample'.format(ts_id),
            query_string={
                'freq': 'min', 'aggregation': 'mean',
                'unit': 'DegreeFahrenheit',
                'start_time': t_start, 'end_time': t_h1_dt.isoformat(), })
        assert response.status_code == 200
        ts_list = response.json['data']
        for idx, row in enumerate(ts_list):
            expected_value = celsius_to_fahrenheit(value_l[idx])
            assert row['value'] == expected_value
        # Get data, converting to a not compatible unit
        response = self.client.get(
            '/timeseries/{}/resample'.format(ts_id),
            query_string={
                'freq': 'min', 'aggregation': 'mean', 'unit': 'Meter',
                'start_time': t_start, 'end_time': t_h1_dt.isoformat(), })
        assert response.status_code == 422
        # Get data, converting to an unknown unit
        response = self.client.get(
            '/timeseries/{}/resample'.format(ts_id),
            query_string={
                'freq': 'min', 'aggregation': 'mean', 'unit': 'zblorg',
                'start_time': t_start, 'end_time': t_h1_dt.isoformat(), })
        assert response.status_code == 422

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_timeseries_stats(self):
        """Check timeseries stats view"""

        ts_id = 'Test_1'
        t_start = dt.datetime(2017, 1, 1).isoformat()
        t_end = dt.datetime(2017, 6, 1).isoformat()
        # Note: we add TZ info here for later comparison with API output:
        # timestamps are serialized as TZ aware UTC
        timestamp_l = [
            (dt.datetime(2017, 1, 1, tzinfo=tzutc()) +
             dt.timedelta(n)).isoformat()
            for n in range(5)]
        value_l = range(5)
        data_list_v = [
            {'timestamp': t, 'value': v}
            for t, v in zip(timestamp_l, value_l)
        ]

        # No data
        response = self.client.get(
            '/timeseries/{}/stats'.format(ts_id))
        assert response.status_code == 200
        resp = response.json
        assert resp == {'count': 0}

        # Set data
        response = self.patch_item(ts_id, data=data_list_v)
        assert response.status_code == 204

        # Get stats
        response = self.client.get(
            '/timeseries/{}/stats'.format(ts_id))
        assert response.status_code == 200
        resp = response.json
        assert 'update_ts' in resp
        del resp['update_ts']
        assert resp == {
            'count': 5,
            'start_time': '2017-01-01T00:00:00+00:00',
            'end_time': '2017-01-05T00:00:00+00:00'}

        # Get stats
        response = self.client.get(
            '/timeseries/{}/stats'.format(ts_id),
            query_string={'start_time': t_start, 'end_time': t_end})
        assert response.status_code == 200
        resp = response.json
        assert 'update_ts' in resp
        del resp['update_ts']
        assert resp == {
            'count': 5,
            'start_time': '2017-01-01T00:00:00+00:00',
            'end_time': '2017-01-05T00:00:00+00:00'}

    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_views_timeseries_aggregate(self, init_db_data):
        """Check timeseries aggregate view"""
        def generate_data(t_start, t_end, rng=False):
            for num in range(4):
                # Get timeserie id
                db_data = init_db_data
                measure_id = str(db_data['measures'][num])

                response = self.get_item_by_id(
                    uri='/measures/', item_id=measure_id)
                assert response.status_code == 200
                ts_metadata = response.json
                ts_id = ts_metadata['external_id']

                # Generate index
                timestamp_l = pd.date_range(
                    t_start, t_end, freq='10T', closed='left')
                # Generate data
                if rng:
                    value_l = map(float, np.random.rand(
                        len(timestamp_l)) * 100)
                    quality_l = map(float, np.random.randint(
                        2, size=len(timestamp_l)))
                else:
                    value_l = range(len(timestamp_l))
                    quality_l = [i % 2 for i in range(len(timestamp_l))]

                data_list = [
                    {'timestamp': t.isoformat(), 'value': v, 'quality': q}
                    for t, v, q in zip(timestamp_l, value_l, quality_l)
                ]

                # Set data
                response = self.patch_item(ts_id, data=data_list)
                assert response.status_code == 204
                yield ts_id, data_list

        # print('# Generate data')
        t_start = dt.datetime(2018, 1, 1, tzinfo=tzutc())
        t_start_iso = t_start.isoformat()
        t_end = dt.datetime(2018, 1, 15, tzinfo=tzutc())
        ts_id_l, ts_data_l = zip(*generate_data(t_start, t_end, rng=True))

        # print('# Aggregate values')
        # Aggregate values manualy with freq_delta = (1h / 10min = 6)
        freq_delta = 6
        values = np.nansum(np.array([
            [
                np.nansum(
                    [item['value'] for item in ts_data[i: i + freq_delta]])
                for i in range(len(ts_data))
                if (i % freq_delta) == 0
            ]
            for ts_data in ts_data_l
        ]), axis=0)

        qualities = np.nansum(np.array([
            [
                np.nansum([
                    item['quality']
                    for item in ts_data[i: i + freq_delta]]) / freq_delta
                for i in range(len(ts_data))
                if (i % freq_delta) == 0
            ]
            for ts_data in ts_data_l
        ]), axis=0) / 4

        # print('# Tests')
        # Test aggregated data: freq=1h agg=sum
        response = self.client.get(
            '/timeseries/aggregate',
            query_string={
                'ts_ids': ts_id_l,
                'start_time': t_start, 'end_time': t_end, 'freq': 'hour',
                'resampling_method': 'sum', 'operation': 'sum'})
        assert response.status_code == 200
        resp_data = response.json['data']
        assert resp_data[0]['timestamp'] == t_start_iso
        # Take random sample in response and compare to calculated values
        #  and qualities
        idxs = random.sample(range(len(resp_data)), int(len(resp_data) / 10))
        for idx in idxs:
            assert isclose(resp_data[idx]['value'], values[idx])
            assert isclose(resp_data[idx]['quality'], qualities[idx])

        # Test with empty timeserie id
        response = self.client.get(
            '/timeseries/aggregate',
            query_string={
                'ts_ids': [],
                'start_time': t_start, 'end_time': t_end, 'freq': 'hour',
                'resampling_method': 'sum', 'operation': 'sum'})
        assert response.status_code == 422

        # Test with invalid timeserie id
        response = self.client.get(
            '/timeseries/aggregate',
            query_string={
                'ts_ids': ['_notexist', '_notexist2'],
                'start_time': t_start, 'end_time': t_end, 'freq': 'hour',
                'resampling_method': 'sum', 'operation': 'sum'})
        assert response.status_code == 404

        # Test with duplicate timeserie id
        response = self.client.get(
            '/timeseries/aggregate',
            query_string={
                'ts_ids': ts_id_l + ts_id_l,
                'start_time': t_start, 'end_time': t_end, 'freq': 'hour',
                'resampling_method': 'sum', 'operation': 'sum'})
        assert response.status_code == 200

        # Test with invalid aggregation method
        response = self.client.get(
            '/timeseries/aggregate',
            query_string={
                'ts_ids': ts_id_l,
                'start_time': t_start, 'end_time': t_end, 'freq': 'hour',
                'resampling_method': 'sum', 'operation': 'thisiswrong'})
        assert response.status_code == 422

        # Test with invalid aggregation method
        response = self.client.get(
            '/timeseries/aggregate',
            query_string={
                'ts_ids': ts_id_l,
                'start_time': t_start, 'end_time': t_end, 'freq': 'hour',
                'resampling_method': 'thisiswrong', 'operation': 'sum'})
        assert response.status_code == 422

        # Test with time selection with no data
        t_start = dt.datetime(2015, 1, 1, tzinfo=tzutc())
        t_end = dt.datetime(2015, 1, 15, tzinfo=tzutc())
        response = self.client.get(
            '/timeseries/aggregate',
            query_string={
                'ts_ids': ts_id_l,
                'start_time': t_start, 'end_time': t_end, 'freq': 'hour',
                'resampling_method': 'sum', 'operation': 'sum'})
        assert response.status_code == 200
        assert len(response.json['data']) == 0

        # Test with time selection with partial data
        t_start = dt.datetime(2017, 12, 15, tzinfo=tzutc())
        t_end = dt.datetime(2018, 1, 15, tzinfo=tzutc())
        response = self.client.get(
            '/timeseries/aggregate',
            query_string={
                'ts_ids': ts_id_l,
                'start_time': t_start, 'end_time': t_end, 'freq': 'day',
                'resampling_method': 'sum', 'operation': 'sum'})
        assert response.status_code == 200
        assert len(response.json['data']) == 14

    @pytest.mark.usefixtures('init_app', 'init_db_data')
    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_timeseries_tsload_duplicate_indexes(self):
        """Check timeseries handling of duplicate indexes"""
        ts_id = 'Test_1'
        timestamp_l = [
            dt.datetime(2017, 1, 1).isoformat(),
            dt.datetime(2017, 1, 1).isoformat(),
            dt.datetime(2017, 1, 2).isoformat(),
        ]
        value_l = [0, 1, 2]
        data_list = [
            {'timestamp': t, 'value': v}
            for t, v in zip(timestamp_l, value_l)
        ]
        response = self.patch_item(ts_id, data=data_list)
        assert response.status_code == 422
        assert response.json['errors'] == {'data': '1 duplicate indexe(s)'}

    @pytest.mark.parametrize('init_db_data', [
        {'gen_sensors': True, 'gen_measures': True}], indirect=True)
    def test_timeseries_clean_ugly_hack(self, init_db_data):
        """Check the TS_ID@clean trick works and does not pollute TS_ID"""

        db_data = init_db_data
        measure_id = str(db_data['measures'][0])

        response = self.get_item_by_id(uri='/measures/', item_id=measure_id)
        assert response.status_code == 200
        ts_metadata = response.json
        ts_id = ts_metadata['external_id']
        ts_id_clean = ts_id + '@clean'

        t_start = dt.datetime(2017, 1, 1).isoformat()
        t_end = dt.datetime(2017, 6, 1).isoformat()
        # Note: we add TZ info here for later comparison with API output:
        # timestamps are serialized as TZ aware UTC
        timestamp_l = [
            (dt.datetime(2017, 1, 1, tzinfo=tzutc()) +
             dt.timedelta(n)).isoformat()
            for n in range(5)]
        value_l = [0, 1, 2, 3, 4]

        data_list_v = [
            {'timestamp': t, 'value': v}
            for t, v in zip(timestamp_l, value_l)
        ]

        # Set data on clean TS
        response = self.patch_item(ts_id_clean, data=data_list_v)
        assert response.status_code == 204

        # Get data on clean TS
        response = self.get_item_by_id(
            item_id=ts_id_clean, start_time=t_start, end_time=t_end)
        assert response.status_code == 200
        ts_list = response.json['data']
        assert len(ts_list) == 5
        assert all(len(v) == 4 for v in ts_list)
        assert [v['timestamp'] for v in ts_list] == timestamp_l
        assert [v['value'] for v in ts_list] == value_l

        # Get data on TS -> empty
        response = self.get_item_by_id(
            item_id=ts_id, start_time=t_start, end_time=t_end)
        assert response.status_code == 200
        ts_list = response.json['data']
        assert not ts_list

    @pytest.mark.parametrize('init_db_data', [{
        'gen_services': True, 'gen_outputs': True, 'gen_sensors': True,
        'gen_measures': True,
        }], indirect=True)
    def test_timeseries_id_from_ontology(self, init_db_data):
        db_data = init_db_data
        output_id = str(db_data['outputs'][-1])
        measure_id = str(db_data['measures'][0])

        response = self.get_item_by_id(uri='/measures/', item_id=measure_id)
        ts_id = response.json['external_id']
        response = self.client.get('/timeseries/{}/stats'.format(ts_id))
        assert response.status_code == 200

        response = self.get_item_by_id(
            uri='/outputs/timeseries/', item_id=output_id)
        ts_id = response.json['external_id']
        response = self.client.get('/timeseries/{}/stats'.format(ts_id))
        assert response.status_code == 200
