"""Data model for geography"""

from .thing import Thing


class GeographicInfo(Thing):
    """Geographic info model class"""

    def __init__(self, latitude, longitude, altitude=None, hemisphere=None,
                 climate=None):
        """Constructor for geographic information.

        :param float latitude: the latitude of the position.
        :param float longitude: the longitude of the position.
        :param float altitude: the altitude of the position.
        :param str hemisphere: hemisphere (`Northern` or `Southern`).
        :param str climate: an URI or unique id pointing to a particular
            instance on data model.
        """
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.hemisphere = hemisphere
        self.climate = climate

    @property
    def coordinates(self):
        """Return a pair value for latitude and longitude.

        :return [latitude, longitude]: expressed as float.
        """
        return [self.latitude, self.longitude]
