"""Fixtures for file storage manager tests."""

from io import BytesIO
import pytest

from tests.utils import zip_file_stream, build_data_samples_path


@pytest.fixture()
def ifc_file_data(request):
    """Return a sample IFC file data."""
    with open(build_data_samples_path('sample_test.ifc'), 'r') as ifc_file:
        file_content = ifc_file.read()
    return ('sample.ifc', file_content,)


@pytest.fixture()
def ifc_file_data_stream(request):
    """Return a file data stream."""
    file_name, file_content = ifc_file_data(request)
    return (file_name, BytesIO(bytes(file_content, 'utf-8')),)


@pytest.fixture(params=['.zip'])
def ifc_zip_file_data(request):
    """Return an IFC sample, in a zipped format."""
    file_name, file_content = ifc_file_data(request)
    return (
        '{}{}'.format(file_name, request.param),
        zip_file_stream(file_name, file_content),
    )


@pytest.fixture(params=['.zip'])
def ifc_multi_zip_file_data(request):
    """Return 2 IFC samples, in a zipped format."""
    file_name, file_content = ifc_file_data(request)

    zip_file_content = None
    for i in range(2):
        in_file_name = '{:02d}_{}'.format(i, file_name)
        zip_file_content = zip_file_stream(
            in_file_name, file_content, memory_file=zip_file_content)

    return ('{}{}'.format(file_name, request.param), zip_file_content,)
