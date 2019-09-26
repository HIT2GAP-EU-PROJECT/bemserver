"""Data model for occupancy"""

import abc

from .thing import Thing


class Service(Thing):
    """Description of a service"""

    def __init__(self, name, kind=None, description=None, url=None,
                 model_ids=None, has_frontend=False, site_ids=None, *,
                 id=None):
        super().__init__(id=id)
        self.name = name
        self.description = description
        self.kind = kind
        self.has_frontend = has_frontend
        self.site_ids = site_ids or []
        self.url = url
        self.model_ids = model_ids or []


class Model(Thing):
    """Model class"""

    def __init__(self, name, service_id, description=None, parameters=None,
                 event_output_ids=None, timeseries_output_ids=None, *,
                 id=None):
        super().__init__(id=id)
        self.name = name
        self.description = description
        self.service_id = service_id
        self.parameters = parameters or []
        self.event_output_ids = event_output_ids or []
        self.timeseries_output_ids = timeseries_output_ids or []

    def get_set_of_parameters(self):
        """Returns the list of parameters as a set of pairs (name, value)"""
        return set([(param.name, param.value) for param in self.parameters])


class Parameter:
    """Parameter class"""

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Output(Thing):
    """Output class"""

    @abc.abstractmethod
    def __init__(self, module_id, model_id, *, id=None):
        super().__init__(id=id)
        self.module_id = module_id
        self.model_id = model_id


class OutputEvent(Output):
    """Output event class"""

    def __init__(self, module_id, model_id, *, id=None):
        super().__init__(module_id, model_id, id=id)


class ValuesDescription:
    """Description of the data generated as time series"""

    def __init__(self, kind, unit, sampling=None):
        self.kind = kind
        self.unit = unit
        self.sampling = sampling


class OutputTimeSeries(Output):
    """Output time series"""

    def __init__(self, module_id, model_id, localization, values_desc,
                 *, external_id=None, id=None):
        super().__init__(module_id, model_id, id=id)
        self.localization = localization
        self.values_desc = values_desc
        self.external_id = external_id
