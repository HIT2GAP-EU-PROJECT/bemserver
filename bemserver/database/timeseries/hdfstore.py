"""Pandas/PyTables HDFStore timeseries database manager"""

from contextlib import contextmanager
import threading
import datetime as dt
from pathlib import Path
import warnings

import pandas as pd
from tables import NaturalNameWarning

from bemserver.models.timeseries import Timeseries

from .base import TimeseriesMgr


# XXX: useless?
pd.set_option('io.hdf.default_format', 'table')


# TODO: If we split the data in several files, we'll need several locks
# HDF_LOCKS = defaultdict(threading.Lock)
HDF_LOCK = threading.Lock()
COMPLEVEL = 9
COMPLIB = 'zlib'


@contextmanager
def locked_store(file_path):
    # http://pandas-docs.github.io/pandas-docs-travis/io.html#caveats
    # If you use locks to manage write access between multiple processes,
    # you may want to use fsync() before releasing write locks.
    # For convenience you can use store.flush(fsync=True) to do this for you.
    with HDF_LOCK:
        # Always open in 'a' mode to ensure 'read' works even if file missing
        with pd.HDFStore(
                file_path, mode='a', complevel=COMPLEVEL, complib=COMPLIB
                ) as store:
            yield store
            store.flush(fsync=True)


class HDFStoreTimeseriesMgr(TimeseriesMgr):
    """HDFStore timeseries manager

    Uses HDFStore from Pandas/PyTable

    :param str dir_path: Path to storage directory
    """

    def __init__(self, dir_path):
        self.storage_dir = Path(dir_path)

    def file_path(self, site, ts_id):
        # Clean site and ts_id to avoid trying to write in '/'
        site = site.lstrip('/')
        ts_id = ts_id.lstrip('/')
        site_dir = self.storage_dir / site
        site_dir.mkdir(exist_ok=True)
        # str() is needed for Python < 3.6
        # https://stackoverflow.com/a/42961904
        return str(site_dir / ('{}.hdf5'.format(ts_id)))

    def get(self, site, ts_id, *, t_start=None, t_end=None):
        with locked_store(self.file_path(site, ts_id)) as store:
            # TODO: use a try/catch?
            # https://github.com/pandas-dev/pandas/issues/17912
            if ts_id not in store:
                return Timeseries()
            # Turn t_start and t_end into a condition string
            kwargs = {}
            bounds = []
            if t_start:
                bounds.append('index>=t_start')
            if t_end:
                bounds.append('index<t_end')
            if bounds:
                kwargs['where'] = ' and '.join(bounds)
            sel_df = store.select(ts_id, **kwargs)
            sel_df.sort_index(inplace=True)
            # XXX: Convert all NaN to 1 in quality column.
            # This shouldn't be needed on a new database. It is needed for
            # quality recorded before the default was set.
            sel_df['quality'].fillna(1, inplace=True)
            return Timeseries.from_dataframe(sel_df)

    def set(self, site, ts_id, ts_obj):
        with locked_store(self.file_path(site, ts_id)) as store:
            # Silently ignore empty dataframeframes
            if ts_obj.dataframe.empty:
                return
            # Set update timestamp
            ts_obj.set_update_timestamp(dt.datetime.utcnow())
            # Remove row if index in new data, then add all new data
            # https://stackoverflow.com/a/45642486
            # TODO: data_columns=True?
            # http://pandas.pydata.org/pandas-docs/stable/generated/
            #   pandas.HDFStore.append.html
            if ts_id in store:
                store.remove(
                    ts_id,
                    where=store[ts_id].index.isin(ts_obj.dataframe.index))
            # XXX: We may use TS ID that include dots or other wrong chars...
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=NaturalNameWarning)
                store.append(ts_id, ts_obj.dataframe)

    def delete(self, site, ts_id, t_start, t_end):
        with locked_store(self.file_path(site, ts_id)) as store:
            if ts_id in store:
                where = 'index>=t_start and index<t_end'
                store.remove(ts_id, where=where)
