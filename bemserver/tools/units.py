"""This module provides units"""

from pint import UnitRegistry, errors  # noqa


# Create registry
ureg = UnitRegistry()

# Define custom units
ureg.define('percent = 0.01*count')
ureg.define('permille= 0.001*count')
ureg.define('ppm = 0.000001*count')


def get_pint_unit(unit):
    """Return the Pint unit name corresponding to given Hit2Gap's unit name.

        ..Note:
            Unit symbols format are pretty `pint` specific, even if based
            on the International System of Units.
            For example:
                - celcius degrees symbol is 'degC'
                - fahrenheit degrees symbol is 'degF'
                - and so on...
            See https://github.com/hgrecco/pint/blob/master/pint/default_en.txt

    :param str unit: Hit2Gap's unit name (as defined in the ontology).
    :return str: Pint unit name (international symbols) or None.
    """
    units = {
        'DegreeCelsius': 'degC',
        'DegreeFahrenheit': 'degF',
        'Kelvin': 'degK',
        'Percent': 'percent',
        'Permille': 'permille',
        'Pascal': 'pascal',
        'HectoPascal': 'hectopascal',
        'AtmosphereStandard': 'atmosphere',
        'Bar': 'bar',
        'PartsPerMillion': 'ppm',
        'LiterPerSecond': 'liter / second',
        'CubicMeterPerSecond': 'meter**3 / second',
        'CubicMeterPerHour': 'meter**3 / hour',
        'MeterPerSecond': 'meter / second',
        'KilogramPerSecond': 'kilogram / second',
        'Watt': 'watt',
        'Kilowatt': 'kilowatt',
        'Ampere': 'ampere',
        'Volt': 'volt',
        'Meter': 'meter',
        'Millimeter': 'mm',
        'CubicMillimeter': 'mm**3',
        'CubicMeter': 'meter**3',
        'Megawatthour': 'megawatt_hour',
        'Kilowatthour': 'kilowatt_hour',
        'watthour': 'watt_hour',
        'Joule': 'joule',
        'GigaJoule': 'gigajoule',
        'KilowattSquareMeter': 'kilowatt / meter**2',
        'WattSquareMeter': 'watt / meter**2',
        'Lux': 'lux',
        'Number': 'dimensionless',
        'Unitless': 'dimensionless',
        'Hour': 'hour',
        'JoulePerSquareCentimeter': 'joule / cm**2',
        'KiloJoulePerKilogram': 'kilojoule / kilogram',
    }
    return units.get(unit)
