"""Timeseries exceptions"""


class TimeseriesError(Exception):
    """Generic Timeseries error"""


class TimeseriesInvalidIndexTypeError(TimeseriesError, ValueError):
    """Invalid index type in timeseries: should bea DatetimeIndex"""


class TimeseriesMissingColumnError(TimeseriesError, ValueError):
    """Missing column in timeseries"""


class TimeseriesInvalidColumnsError(TimeseriesError, ValueError):
    """Invalid columns in timeseries"""


class TimeseriesUnitConversionError(TimeseriesError):
    """Invalid unit conversion data in timeseries."""
