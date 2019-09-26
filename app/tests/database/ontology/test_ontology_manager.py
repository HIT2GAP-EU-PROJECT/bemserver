"""Tests for a Jena manager"""

import logging
from unittest import mock
import pytest
from bemserver.database.ontology.exceptions import SPARQLError
from bemserver.database.ontology.manager import (
    PREFIX, SPARQLOP, ontology_manager_factory)

from tests import TestCoreDatabaseOntology


class TestOntologyManagerPrefixEnum():
    """Unit test for PREFIX"""

    def test_ontology_manager_prefix_enum_alias_uri(self):
        assert PREFIX.ROOT.alias_uri('lol') == 'bem:lol'

    def test_ontology_manager_prefix_enum_get_name(self):
        assert PREFIX.get_name(
            'http://qudt.org/schema/qudt#lol') == 'lol'
        with pytest.raises(ValueError):
            PREFIX.get_name('dummy')
            PREFIX.get_name('du#mm#y')


@pytest.mark.usefixtures('init_onto_mgr_fact')
class TestOntologyManager(TestCoreDatabaseOntology):
    """Tests on Jena manager"""

    def test_ontology_manager(self):

        onto_mgr = ontology_manager_factory.get_ontology_manager()

        def count_values():
            """Simple method to count values"""
            result = onto_mgr.perform(
                SPARQLOP.SELECT,
                """
PREFIX ifc:<http://www.buildingsmart-tech.org/ifcOWL/IFC2X3_Final#>
SELECT ?elt
WHERE {?elt a ifc:IfcSite}
                """)
            return len(result.values)

        count = count_values()
        onto_mgr.perform(
            SPARQLOP.INSERT,
            """
PREFIX ifc:<http://www.buildingsmart-tech.org/ifcOWL/IFC2X3_Final#>
INSERT DATA
{_:site1 a ifc:IfcSite}
            """)
        assert count_values() == count + 1

    def test_ontology_manager_exceptions(self):

        logger = logging.getLogger('bemserver')

        onto_mgr = ontology_manager_factory.get_ontology_manager()

        # Bad operator
        with pytest.raises(SPARQLError):
            onto_mgr.perform('dummy_op', 'dummy_query')

        # Query bad formed
        with mock.patch.object(logger, 'error') as mock_error:
            with pytest.raises(SPARQLError):
                onto_mgr.perform(SPARQLOP.SELECT, 'SELECT dummy_query')
            assert mock_error.called

        # Endpoint not found
        wrong_url = ontology_manager_factory.base_url[:-1] + 'dummy/'
        ontology_manager_factory.open(wrong_url)
        onto_mgr = ontology_manager_factory.get_ontology_manager()
        with mock.patch.object(logger, 'error') as mock_error:
            with pytest.raises(SPARQLError):
                onto_mgr.perform(
                    SPARQLOP.SELECT, 'SELECT * WHERE { ?s ?p ?o }')
            assert mock_error.called
