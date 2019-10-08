"""Data model for energy"""

from ..tools.custom_enum import HierarchyEnum


class EnergyCategory(HierarchyEnum):
    """Renewable energy categories (based on OntoMG ontology)"""

    # solar
    solar = ('Solar', None, True)
    solar_thermal = ('Solar thermal', 'solar', True)
    solar_photovoltaic = ('Photovoltaic', 'solar', True)

    # wind
    wind = ('Wind', None, True)

    # hydropower
    hydropower = ('Hydropower', None, True)
    hydropower_potential = ('Potential', 'hydropower', True)
    hydropower_wave_power = ('Wave power', 'hydropower', True)
    hydropower_tidal_power = ('Tidal power', 'hydropower', True)
    hydropower_thermal = ('Thermal', 'hydropower', True)
    hydropower_osmotic = ('Osmotic', 'hydropower', True)

    # geothermal
    geothermal = ('Geothermal', None, True)

    # biomass
    biomass = ('Biomass', None, True)
    biomass_wood = ('Wood', 'biomass', True)
    biomass_biogas = ('Biogas', 'biomass', True)
    biomass_biofuel = ('Biofuel', 'biomass', True)

    # oil
    oil = ('Oil', None, False)
    oil_gasoline = ('Gasoline', 'oil', False)
    oil_diesel = ('Diesel', 'oil', False)
    oil_heating_oil = ('Heating oil', 'oil', False)

    # gas
    gas = ('Gas', None, False)
    gas_hydrocarbon_gas = ('Hydrocarbon gas', 'gas', False)
    gas_natural_gas = ('Natural gas', 'gas', False)

    # coal
    coal = ('Coal', None, False)

    # nuclear
    nuclear = ('Nuclear', None, False)

    # grid
    grid = ('Grid', None, False)

    def __init__(self, label, parent_name=None, is_renewable=False):
        HierarchyEnum.__init__(self, label=label, parent_name=parent_name)
        self.is_renewable = is_renewable
        # when self has parent, check is_renewable consistency
        cur_item = self
        while cur_item.has_parent:
            cur_item = cur_item.parent
            if is_renewable != cur_item.is_renewable:
                raise ValueError(
                    'Invalid {} "is_renewable" value relative to its parent {}'
                    .format(self, cur_item))

    @classmethod
    def get_renewables(cls):
        """Return only renewables energy categories"""
        return [item for item in cls if item.is_renewable]

    @classmethod
    def get_non_renewables(cls):
        """Return only non renewables energy categories"""
        return [item for item in cls if not item.is_renewable]
