"""Abstract timeseries database manager"""

from abc import ABC, abstractmethod


class TimeseriesMgr(ABC):
    """Timeseries database driver abstract class

    Timeseries are stored as Pandas DataFrame.

    The index is the timestamp of the data (datetime).
    The columns are
    - data: value (float)
    - quality: reliability indicator (float is [0,1] or NaN)
    - update_ts: time of instertion in database (datetime)

    datetime instances can be naive or aware. However,
    - mixing two different timezones in the same column/index is forbidden and
      results in a ValueError,
    - mixing naive and aware datetimes results in naive datetimes turned into
      aware datetimes with the same timezone as the aware ones.

    Bottom line, you'd better stick with naive (implicit UTC) or aware (UTC).
    """

    @abstractmethod
    def get(self, ts_id, t_start, t_end):
        """Get values for a time series in a given interval

        :param str ts_id: Time series ID
        :param datetime t_start: Start time
        :param datetime t_end: End time (exclusive)

        Returns a dataframe with the values for [t_start, t_end)
        """

    @abstractmethod
    def set(self, ts_id, data):
        """Set values for a time series

        :param str ts_id: Time series ID
        :param dataframe data: Data to write. Index should be a DatetimeIndex.
        """

    @abstractmethod
    def delete(self, ts_id, t_start, t_end):
        """Remove values for a time series in a given interval

        :param str ts_id: Time series ID
        :param datetime t_start: Start time
        :param datetime t_end: End time (exclusive)
        """

    # TODO: implement delete_timeseries?
    # @abstractmethod
    def delete_timeseries(self, ts_id):
        raise NotImplementedError
