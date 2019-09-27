"""Tests the interface Modules/DB"""

from uuid import uuid4 as gen_uuid
import pytest

from bemserver.database import ServiceDB, ModelDB, OutputDB
from bemserver.database.exceptions import ItemNotFoundError
from bemserver.models import (
    Service, Model, OutputEvent, OutputTimeSeries, ValuesDescription,
    Parameter)

from tests import TestCoreDatabaseOntology


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestServiceDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle services in the ontology."""

    def test_db_service_get_empty(self):

        service_db = ServiceDB()

        # get all items
        result = service_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            service_db.get_by_id('not_existing')

    def test_db_service_create(self, init_sites):

        service_db = ServiceDB()

        # check that database is empty
        result = service_db.get_all()
        assert list(result) == []

        # create an item

        service = Service('Service#0', url='http://hit2gap.eu/Service#0',
                          description='New sample service',
                          has_frontend=True, site_ids=init_sites)
        new_service_id = service_db.create(service)
        assert new_service_id is not None
        assert new_service_id == service.id

        # check that database is not empty now
        result = service_db.get_all()
        services = list(result)
        assert len(services) == 1
        assert services[0].id == service.id
        assert services[0].name == service.name
        assert services[0].description == service.description
        assert services[0].url == service.url
        assert services[0].has_frontend
        assert set(services[0].site_ids) == set(init_sites)

    def test_db_service_filter(self, init_sites):
        service_db = ServiceDB()

        # check that database is empty
        result = service_db.get_all(name='Service#0')
        assert list(result) == []
        result = service_db.get_all(
            url="http://hit2gap.eu/services/forecasting")
        assert list(result) == []

        # create an item
        service_db.create(
            Service('Service#0', url='http://hit2gap.eu/services/fdd',
                    description='New sample FDD service',
                    site_ids=[str(init_sites[0])]))
        service_db.create(
            Service('Service#1', url='http://hit2gap.eu/services/forecasting',
                    description='New sample forecasting service',
                    has_frontend=True))

        services = list(service_db.get_all())
        assert len(services) == 2
        result = service_db.get_all(name="Service#1")
        assert len(list(result)) == 1

        result = service_db.get_all(
            url="http://hit2gap.eu/services/forecasting")
        assert len(list(result)) == 1

        result = service_db.get_all(site=str(init_sites[0]))
        assert len(list(result)) == 1

        result = service_db.get_all(has_frontend=True)
        assert len(list(result)) == 1

    def test_db_service_update(self, init_services):

        service_ids = init_services
        service_db = ServiceDB()

        # get all items
        result = service_db.get_all()
        services = list(result)
        assert len(services) == 2
        for cur_service in services:
            assert cur_service.id in service_ids

        # get an item by its ID!
        # for a service, the ID to be used is the URL
        service = service_db.get_by_id(services[0].id)

        # update item data
        new_description = 'updated by patator'
        new_name = 'New Name'
        new_url = 'http://sibex.nobatek.inef4.fr/forecasting'

        service.description = new_description
        service.name = new_name
        service.url = new_url
        service_db.update(service.id, service)

        # check that item has really been updated in database
        updated_service = service_db.get_by_id(service.id)
        assert updated_service.id == service.id
        assert updated_service.name == new_name
        assert updated_service.description == new_description
        assert updated_service.url == new_url
        assert updated_service.kind == service.kind == 'Service'
        assert updated_service.model_ids == service.model_ids == []

        # delete an item by its ID
        service_db.remove(service.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            service_db.get_by_id(service.id)


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestModelDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle services in the ontology."""

    def test_db_model_get_empty(self):

        model_db = ModelDB()

        # get all items
        result = model_db.get_all()
        assert list(result) == []

        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            model_db.get_by_id('not_existing')

    def test_db_model_create(self, init_services):

        model_db = ModelDB()

        # check that database is empty
        result = model_db.get_all()
        assert list(result) == []

        # create an item
        model = Model('ARIMA#0', init_services[0],
                      description='A sample model',
                      parameters=[Parameter('ar', 5)])
        new_model_id = model_db.create(model)
        assert new_model_id is not None
        assert new_model_id == model    .id

        # check that database is not empty now
        result = model_db.get_all()
        models = list(result)
        assert len(models) == 1
        assert models[0].id == model.id
        assert models[0].name == model.name
        assert models[0].service_id == model.service_id
        assert models[0].description == model.description
        assert models[0].get_set_of_parameters() == (
            model.get_set_of_parameters())

        # test relation between service and model
        service = ServiceDB().get_by_id(model.service_id)
        assert service.model_ids == [model.id]

    def test_db_model_filter(self, init_services):
        model_db = ModelDB()
        services = init_services

        # check that database is empty
        result = model_db.get_all(name='Model #0')
        assert list(result) == []
        result = model_db.get_all(service_id=str(services[0]))
        assert list(result) == []

        # create an item
        model_db.create(
            Model('Model #0', services[0], description='New sample FDD model',
                  parameters=[Parameter('param1', 1)]))
        model_db.create(
            Model('Model #1', services[0],
                  description='RENew sample FDD model',
                  parameters=[Parameter('param1', 1), Parameter('param2', 2)]))

        models = list(model_db.get_all())
        assert len(models) == 2
        result = model_db.get_all(name="Model #1")
        assert len(list(result)) == 1

        result = model_db.get_all(service_id=services[0])
        assert len(list(result)) == 2

        result = model_db.get_all(service_id=services[1])
        assert len(list(result)) == 0

    def test_db_model_update(self, init_models):
        model_ids, _ = init_models
        model_db = ModelDB()

        # get all items
        result = model_db.get_all()
        models = list(result)
        assert len(models) == 2
        for cur_model in models:
            assert cur_model.id in model_ids

        # get an item by its ID!
        # for a model, the ID to be used is the URL
        model = model_db.get_by_id(models[0].id)

        # update item data
        new_description = 'updated by patator'
        new_name = 'New Name'
        new_parameters = [Parameter('NewParam', 0)]
        model.description = new_description
        model.name = new_name
        model.parameters = new_parameters
        model_db.update(model.id, model)

        # check that item has really been updated in database
        updated_model = model_db.get_by_id(model.id)
        assert updated_model.id == model.id
        assert updated_model.name == new_name
        assert updated_model.description == new_description
        assert updated_model.service_id == model.service_id
        assert set(updated_model.event_output_ids) ==\
            set(model.event_output_ids)
        assert set(updated_model.timeseries_output_ids) ==\
            set(model.timeseries_output_ids)

        assert updated_model.get_set_of_parameters() ==\
            model.get_set_of_parameters() == set([('NewParam', 0)])

        # delete an item by its ID
        model_db.remove(model.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            model_db.get_by_id(model.id)


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestOutputDB(TestCoreDatabaseOntology):
    """Tests on the interface to handle services in the ontology."""

    def test_db_output_get_empty(self):
        output_db = OutputDB()
        # get all items
        result = output_db.get_all()
        assert list(result) == []
        # try to get an inexistant item
        with pytest.raises(ItemNotFoundError):
            output_db.get_by_id('not_existing')

    def test_db_output_create(self, init_models, init_buildings):
        building_ids, _ = init_buildings
        output_db = OutputDB()
        # check that database is empty
        result = output_db.get_all()
        assert list(result) == []

        # get service and model id
        models = list(ModelDB().get_all())
        model_id, service_id = models[0].id, models[0].service_id

        # create an item
        output = OutputEvent(service_id, model_id, id=str(gen_uuid()))
        new_output_id_evt = output_db.create(output)
        assert new_output_id_evt is not None

        # check that database is not empty now
        result = output_db.get_all()
        outputs = list(result)
        assert len(outputs) == 1
        assert outputs[0].module_id == service_id
        assert outputs[0].model_id == model_id

        # test with time series
        output = OutputTimeSeries(
            service_id, model_id, building_ids[0],
            ValuesDescription('Temperature', 'DegreeCelsius', 20),
            id=str(gen_uuid()))
        new_output_id_ts = output_db.create(output)
        assert new_output_id_ts is not None

        result = output_db.get_all()
        outputs = list(result)
        assert len(outputs) == 2
        output_event = (
            outputs[0]
            if isinstance(outputs[0], OutputTimeSeries) else outputs[1])
        assert output_event.module_id == service_id
        assert output_event.model_id == model_id
        assert output_event.localization == output.localization
        assert output_event.values_desc.unit == output.values_desc.unit
        assert output_event.values_desc.kind == output.values_desc.kind
        assert output_event.values_desc.sampling == output.values_desc.sampling

        # test relation between service and output
        model = ModelDB().get_by_id(model_id)
        assert set(model.event_output_ids) == {new_output_id_evt}
        assert set(model.timeseries_output_ids) == {new_output_id_ts}

    def test_db_output_filter(self, init_models, init_buildings):
        building_ids, _ = init_buildings
        output_db = OutputDB()

        # get service and model id
        models = list(ModelDB().get_all())
        model_id, service_id = models[0].id, models[0].service_id

        # check that database is empty
        result = output_db.get_all(module_id=service_id)
        assert list(result) == []
        result = output_db.get_all(kind='Temperature')
        assert list(result) == []

        # create an item
        output_db.create(OutputEvent(service_id, model_id))
        output_db.create(
            OutputTimeSeries(
                service_id, model_id, building_ids[0],
                ValuesDescription('Temperature', 'DegreeCelsius', 20)))

        outputs = list(output_db.get_all())
        assert len(outputs) == 2
        result = output_db.get_all(module_id=service_id)
        assert len(list(result)) == 2

        result = output_db.get_all(localization=building_ids[0])
        assert len(list(result)) == 1

        result = output_db.get_all(value_type='Temperature')
        assert len(list(result)) == 1

    def test_db_output_update(self, init_models, init_buildings):
        building_ids, _ = init_buildings

        models = list(ModelDB().get_all())
        model_id, service_id = models[0].id, models[0].service_id

        output_db = OutputDB()
        output = OutputTimeSeries(
            service_id, model_id, building_ids[0],
            ValuesDescription('Temperature', 'DegreeCelsius', 20),
            id=str(gen_uuid()))
        new_output_id_ts = output_db.create(output)

        # get all items
        result = output_db.get_all()
        outputs = list(result)
        assert len(outputs) == 1
        assert [item.id for item in outputs] == [new_output_id_ts]

        # get an item by its ID!
        # for a output, the ID to be used is the URL
        output = output_db.get_by_id(outputs[0].id)

        # update item data
        new_sampling = 400
        new_model_id = models[1].id
        new_kind = 'Energy'
        new_unit = 'Joule'
        output.sampling = new_sampling
        output.model_id = new_model_id
        output.values_desc.kind = new_kind
        output.values_desc.unit = new_unit
        output_db.update(output.id, output)

        # check that item has really been updated in database
        updated_output = output_db.get_by_id(output.id)
        assert updated_output.id == output.id
        assert updated_output.model_id == new_model_id
        assert updated_output.module_id == output.module_id
        assert updated_output.localization == output.localization
        assert updated_output.values_desc.unit == new_unit
        assert updated_output.values_desc.kind == new_kind
        assert updated_output.values_desc.sampling == (
            output.values_desc.sampling)

        # delete an item by its ID
        output_db.remove(output.id)

        # get an item by its ID
        with pytest.raises(ItemNotFoundError):
            # it has been removed...
            output_db.get_by_id(output.id)
