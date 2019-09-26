"""Tests for geo location tools"""

from math import isclose

import pytest
from bemserver.tools.geo_location import (
    convert_dms_to_dd, deduce_hemisphere_from_dms, deduce_hemisphere_from_dd)

from tests import TestCoreTools


class TestToolsGeoLocation(TestCoreTools):
    """Tests geo location tools"""

    def test_tools_geo_location_convert_dms_to_dd(self):
        """Test DMS to DD position converter"""

        # passing args separately: degrees, minutes, seconds, frac_seconds
        latitude = convert_dms_to_dd(51, 29, 59, 999999)
        longitude = convert_dms_to_dd(0, -6, -57, -599999)
        assert isclose(latitude, 51.5)
        assert isclose(longitude, -0.116)

        # passing args in a tuple: (degrees, minutes, seconds, frac_seconds)
        latitude = convert_dms_to_dd((51, 29, 59, 999999))
        longitude = convert_dms_to_dd((0, 6, 57, 599999))
        assert isclose(latitude, 51.5)
        assert isclose(longitude, 0.116)

        # passing args the 2 ways: optional frac_seconds
        latitude = convert_dms_to_dd(51, 29, 59)
        longitude = convert_dms_to_dd((0, -6, -57))
        assert isclose(latitude, 51.4997)
        assert isclose(longitude, -0.1158)

    def test_tools_geo_location_deduce_hemisphere(self):
        """Test deducing hemisphere from positions"""

        # deducing from DMS position
        # passing args separately: degrees, minutes, seconds, frac_seconds
        hemisphere = deduce_hemisphere_from_dms(0, -6, -57, -599999)
        assert hemisphere == 'S'
        # passing args in a tuple: (degrees, minutes, seconds, frac_seconds)
        hemisphere = deduce_hemisphere_from_dms(0, 6, 57, 599999)
        assert hemisphere == 'N'

        # deducing from DMS position
        # passing args the 2 ways: optional frac_seconds
        hemisphere = deduce_hemisphere_from_dms(0, -6, -57)
        assert hemisphere == 'S'
        hemisphere = deduce_hemisphere_from_dms((0, 6, 57))
        assert hemisphere == 'N'

        # deducing from DD position
        hemisphere = deduce_hemisphere_from_dd(-0.116)
        assert hemisphere == 'S'
        hemisphere = deduce_hemisphere_from_dd(0.116)
        assert hemisphere == 'N'

    def test_tools_geo_location_errors(self):
        """Test on errors"""

        # wrong args (DMS values must be 3 or 4 floats as is or in a tuple)
        with pytest.raises(TypeError):
            convert_dms_to_dd()
        with pytest.raises(TypeError):
            convert_dms_to_dd(51)
        with pytest.raises(TypeError):
            convert_dms_to_dd(51, 29)
        with pytest.raises(TypeError):
            convert_dms_to_dd(())
        with pytest.raises(TypeError):
            convert_dms_to_dd((51))
        with pytest.raises(TypeError):
            convert_dms_to_dd((51, 29))

        # DMS values must be all positive or negative
        # converting DMS to DD
        with pytest.raises(ValueError):
            convert_dms_to_dd(-51, 29, 59, 999999)
        with pytest.raises(ValueError):
            convert_dms_to_dd(51, -29, 59, 999999)
        with pytest.raises(ValueError):
            convert_dms_to_dd(51, 29, -59, 999999)
        with pytest.raises(ValueError):
            convert_dms_to_dd(51, 29, 59, -999999)

        # deducing hemisphere from DMS
        with pytest.raises(ValueError):
            deduce_hemisphere_from_dms(-51, 29, 59, 999999)
        with pytest.raises(ValueError):
            deduce_hemisphere_from_dms(51, -29, 59, 999999)
        with pytest.raises(ValueError):
            deduce_hemisphere_from_dms(51, 29, -59, 999999)
        with pytest.raises(ValueError):
            deduce_hemisphere_from_dms(51, 29, 59, -999999)
