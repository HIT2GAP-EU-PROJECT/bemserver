"""Test pint custom units"""

from math import isclose
import numpy as np

from bemserver.tools import units

from tests import TestCoreTools


class TestToolsUnits(TestCoreTools):
    """Tests units"""

    def test_units_custom_units(self):
        """Test custom units added to registry"""

        val_pc = 42 * units.ureg.percent
        assert isclose(val_pc, 0.42)
        assert isclose(val_pc.magnitude, 42)
        assert val_pc.units == 'percent'
        val_pm = val_pc.to('permille')
        assert isclose(val_pm, 0.42)
        assert isclose(val_pm.magnitude, 420)
        assert val_pm.units == 'permille'
        val_ppm = val_pc.to('ppm')
        assert isclose(val_ppm, 0.42)
        assert isclose(val_ppm.magnitude, 420000)
        assert val_ppm.units == 'ppm'
        val_dl = val_pc.to('dimensionless')
        assert isclose(val_dl, 0.42)
        assert isclose(val_dl.magnitude, 0.42)
        assert val_dl.units == units.ureg.Unit('dimensionless')

    def test_units_array_from_magnitude(self):
        """Test magnitude is used when creating np.array

        This ensures we don't need to get the 'magnitude' attribute
        when creating an array or a DataFrame
        """

        qa_m = units.ureg.Quantity(np.array(range(5)), 'meter')
        qa_km = qa_m.to('km')

        a_m = np.array(qa_m)
        a_km = np.array(qa_km)

        assert np.all(a_m == range(5))
        assert np.all(1000 * a_km == range(5))
        assert np.all(a_m == 1000 * a_km)

    def test_units_get_pint_unit(self):
        assert units.get_pint_unit('DegreeCelsius') == 'degC'
        assert units.get_pint_unit('Lux') == 'lux'

        assert units.get_pint_unit('unknown') is None
