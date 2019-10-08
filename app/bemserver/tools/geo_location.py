"""Geo location tools"""


def _parse_dms_args(*args):
    """args expected values are:
        a tuple or a list: (degrees, minutes, seconds, [frac_seconds])
        3 or 4 float values: degrees, minutes, seconds, [frac_seconds]
    frac_seconds is optional (his default value is zero)
    """
    if len(args) == 1:
        if (not isinstance(args[0], (tuple, list,))
                or len(args[0]) < 3 or len(args[0]) > 4):
            raise TypeError('Invalid args: {}'.format(args))
        args = args[0]
    if len(args) < 3 or len(args) > 4:
        raise TypeError('Invalid args: {}'.format(args))

    # return degrees, minutes, seconds, frac_seconds
    return args[0], args[1], args[2], args[3] if len(args) == 4 else 0


def _check_dms_consistency(degrees, minutes, seconds, frac_seconds):
    """DMS coordinates direction ('N', 'S', 'E' and 'W') is supposed to be
    included in all values by signing them (positive for 'N' and 'E',
    negative for 'S' and 'W').

    Raises ValueError if this is not respected.
    """
    if ((degrees < 0 and (minutes > 0 or seconds > 0 or frac_seconds > 0)) or
            (degrees > 0 and (minutes < 0 or seconds < 0 or frac_seconds < 0))
       ):
        raise ValueError(
            'Invalid coordinates values, positive/negative inconsistency.')


def convert_dms_to_dd(*args):
    """Convert a Degrees Minutes Seconds (DMS, respect to the world geodetic
    system WGS84) position into a Decimal Degrees (DD) position.

    ::param args::
        expected values are:
            a tuple or a list: (degrees, minutes, seconds, [frac_seconds])
            3 or 4 float values: degrees, minutes, seconds, [frac_seconds]
        frac_seconds is optional (his default value is zero)

    Latitudes are measured relative to the geodetic equator:
        north of the equator by positive values from 0 till +90,
        south of the equator by negative values from 0 till -90.
    Longitudes are measured relative to the geodetic zero meridian, nominally
    the same as the Greenwich prime meridian:
        west of the zero meridian have positive values from 0 till +180,
        east of the zero meridian have negative values from 0 till -180.

    Note: coordinates direction ('N', 'S', 'E' and 'W') is supposed to be
        included in all values by signing them (positive for 'N' and 'E',
        negative for 'S' and 'W').

    Examples:
        DMS latitude 51°29'59"999999 is north -> N
        DMS latitude -51°-29'-59"-999999 is south -> S
        DMS longitude 0°-6'-57"-599999 is west -> W
        DMS longitude 0°6'57"599999 is east -> E
    """
    degrees, minutes, seconds, frac_seconds = _parse_dms_args(*args)
    _check_dms_consistency(degrees, minutes, seconds, frac_seconds)

    seconds = str(seconds) + '.' + str(abs(frac_seconds))
    result = float(degrees) + (float(minutes) / 60) + (float(seconds) / 3600)
    return round(result, 4)


def deduce_hemisphere_from_dms(*args):
    """Return 'N' (north) or 'S' (south) depending on respectively positive or
    negative sign of DMS longitude.
    """
    degrees, minutes, seconds, frac_seconds = _parse_dms_args(*args)
    _check_dms_consistency(degrees, minutes, seconds, frac_seconds)

    if degrees < 0 or minutes < 0 or seconds < 0 or frac_seconds < 0:
        return 'S'
    return 'N'


def deduce_hemisphere_from_dd(decimal_degrees):
    """Return 'N' (north) or 'S' (south) depending on respectively positive or
    negative sign of `decimal_degrees` longitude.
    """
    if decimal_degrees < 0:
        return 'S'
    return 'N'
