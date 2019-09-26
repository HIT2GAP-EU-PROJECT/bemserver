"""Fixtures for import_data basic services tests"""

import pytest

from bemserver.database import DBAccessor, init_handlers

from tests.utils import build_data_samples_path


@pytest.fixture(params=['sample_test.ifc'])
def ifc_filepath(request):
    """Return an IFC file path"""
    return build_data_samples_path(request.param)


@pytest.fixture
def db_accessor():
    '''Creates a well-configured DBAccessor so as to store elements in the data
     model'''
    accessor = DBAccessor()
    accessor.set_handler(init_handlers())
    return accessor
