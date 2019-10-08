"""Tests for energy data model"""

from bemserver.models.energy import EnergyCategory

from tests import TestCoreModel


class TestModelEnergy(TestCoreModel):
    """Energy model tests"""

    def test_model_energy_category_enum(self):
        """Tests on EnergyCategory"""

        # is_renewable or not
        assert EnergyCategory.solar.is_renewable
        assert EnergyCategory.solar_thermal.is_renewable
        assert not EnergyCategory.grid.is_renewable

        # renewables
        assert EnergyCategory.get_renewables() == [
            item for item in EnergyCategory if item.is_renewable]

        # non_renewables
        assert EnergyCategory.get_non_renewables() == [
            item for item in EnergyCategory if not item.is_renewable]

        # hierarchy
        assert not EnergyCategory.solar.has_parent
        assert EnergyCategory.solar_thermal.has_parent
        assert EnergyCategory.solar_thermal.parent == EnergyCategory.solar
