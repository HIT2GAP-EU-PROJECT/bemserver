"""Timeseries API exceptions"""


class TimeseriesAPIError(Exception):
    """Generic timeseries API error"""


class TimeseriesConfigError(TimeseriesAPIError):
    """Timeseries configuration error"""
