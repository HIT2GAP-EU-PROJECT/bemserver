"""Serialization and deserialization functions for Timeseries"""

import datetime as dt
import numpy as np
import pandas as pd
from flask import current_app

from bemserver.database.timeseries.hdfstore import (
    HDFStoreTimeseriesMgr)

from bemserver.models import Timeseries

from .exceptions import TimeseriesConfigError

from ...extensions.rest_api import abort


# TODO: do this at init time?
# TODO: check at init that storage path exists and is writable?

def get_timeseries_manager():
    """Return timeseries manager according to application configuration"""

    app_config = current_app.config

    # Instantiate timeseries manager
    backend = app_config.get('TIMESERIES_BACKEND')
    if backend == 'hdfstore':
        try:
            storage_dir = app_config['TIMESERIES_BACKEND_STORAGE_DIR']
        except KeyError:
            raise TimeseriesConfigError(
                "Missing hdfstore storage directory in configuration")
        timeseries_mgr = HDFStoreTimeseriesMgr(storage_dir)
    else:
        raise TimeseriesConfigError(
            "Invalid timeseries backend: {}".format(backend))

    return timeseries_mgr


def tsload(data_list):
    """Deserialize timeseries values from a dict to a structured DataFrame.

    :param list data_list: Timeseries values (as a list of dicts).
    :return Timeseries: Timeseries values loaded in structured DataFrame.
    """
    if not data_list:
        return Timeseries()

    # Create dataframe and rename columns
    dataframe = pd.DataFrame(data_list)
    dataframe = dataframe.rename(columns={
        'timestamp': Timeseries.TIMESTAMPS_COL,
        'value': Timeseries.DATA_COL,
        'update_ts': Timeseries.UPDATE_TIMESTAMP_COL,
        'quality': Timeseries.QUALITY_COL,
    })

    # Reject if duplicate indexes
    dups = dataframe[Timeseries.TIMESTAMPS_COL].duplicated()
    if any(dups):
        abort(422, errors={'data': '{} duplicate indexe(s)'.format(
            np.count_nonzero(dups))})

    # Create and return timeseries
    return Timeseries.from_dataframe(dataframe)


def tsdump(timeseries, *, to_isotime=False):
    """Serialize timeseries values.

    :param pandas.DataFrame timeseries:
        Timeseries values in a structured DataFrame.
    :param bool to_isotime: (optional, default False)
        If True, datetime objects are converted into ISO 8601 strings.
    :return list: Timeseries values dict structured.
    """
    # Rename columns
    dataframe = timeseries.dataframe.rename(columns={
        Timeseries.DATA_COL: 'value',
        Timeseries.UPDATE_TIMESTAMP_COL: 'update_ts',
        Timeseries.QUALITY_COL: 'quality',
    })
    dataframe.index.names = ['timestamp']

    # Replace null values
    dataframe = dataframe.where((pd.notnull(dataframe)), None)

    # Export as list of dicts
    dataframe.reset_index(inplace=True)
    # Surprisingly, we do not use 'to_dict' pandas's function because of a
    # lack of performance on a huge amount of data. This is due to some
    # genericity features added in 'to_dict' function unneeded for our
    # simple use case (for example, no need to convert datetimes...).
    # Here we could have just written "dataframe.to_dict(orient='records')"...
    result = []
    for src_row in dataframe.values:
        row = {}
        for key, val in zip(dataframe.columns, src_row):
            # Convert datetime objects to ISO strings, if needed
            if to_isotime and key in ('timestamp', 'update_ts',):
                val = val.replace(tzinfo=dt.timezone.utc).isoformat()
            row[key] = val
        result.append(row)

    return result
