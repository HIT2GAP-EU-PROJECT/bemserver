"""A module to extract time-series for unit test prurpose"""

import os
from datetime import datetime
import numpy as np
import pandas as pd


class _DataExtractor(object):
    """A generic class to extract a dataframe from a CSV file"""

    def __init__(self, date_column, file_name, cols=None, convert=True):
        """Constructor"""
        dirname = os.path.dirname(__file__)
        self.filename = os.path.join(dirname, file_name)
        self.datename = date_column
        _cols = cols or []
        self.data = self.__extract([date_column] + _cols, convert)

    def __extract(self, cols, convert):
        if convert:
            return pd.read_csv(
                self.filename, index_col=0,
                dtype={0: datetime, 1: np.float64},
                encoding='latin-1', delimiter=';', usecols=cols,
                parse_dates=True,
                date_parser=lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M'))
        else:
            return pd.read_csv(
                self.filename, index_col=0, encoding='latin-1',
                delimiter=';', usecols=cols, parse_dates=True,
                date_parser=lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M'))

    def get_data(self):
        """To get the data - returns a pandas.Dataframe"""
        return self.data


class DataExtractorPower(_DataExtractor):
    """An extractor of energy consummption data"""

    def __init__(self, convert=True):
        super().__init__('Date',
                         'data_samples/Consumption.csv',
                         cols=['TS2E2 - EV-DRV-UE-TS-N2-02 Puissance kW'],
                         convert=convert)


class DataExtractorTemperature(_DataExtractor):
    """An extractor of temperature data"""

    def __init__(self, startdate, enddate, convert=True):
        super().__init__('Date',
                         'data_samples/temperature.csv',
                         cols=['External Temperature'],
                         convert=convert)
        start = datetime.strptime(startdate, '%d/%m/%Y %H:%M')
        end = datetime.strptime(enddate, '%d/%m/%Y %H:%M')
        self.data = self.data.loc[start:end]
