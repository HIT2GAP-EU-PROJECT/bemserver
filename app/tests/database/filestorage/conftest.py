"""Fixtures for file storage manager tests."""

from io import BytesIO
import pytest

from tests.utils import zip_file_stream, build_data_samples_path


def ifc_file_data():
    """Return a sample IFC file data."""
    with open(build_data_samples_path('sample_test.ifc'), 'r') as ifc_file:
        file_content = ifc_file.read()
    return ('sample.ifc', file_content,)


def ifc_file_data_stream():
    """Return a file data stream."""
    file_name, file_content = ifc_file_data()
    return (file_name, BytesIO(bytes(file_content, 'utf-8')),)


@pytest.fixture(name='ifc_file_data_stream')
def ifc_file_data_stream_fixture():
    """Fixture to return a file data stream."""
    return ifc_file_data_stream()


def ifc_zip_file_data(file_ext):
    """Return an IFC sample, in a zipped format."""
    file_name, file_content = ifc_file_data()
    return (
        '{}{}'.format(file_name, file_ext),
        zip_file_stream(file_name, file_content),
    )


@pytest.fixture(name='ifc_zip_file_data', params=['.zip'])
def ifc_zip_file_data_fixture(request):
    """Fixture to return an IFC sample, in a zipped format."""
    return ifc_zip_file_data(request.param)


def ifc_multi_zip_file_data(file_ext):
    """Return 2 IFC samples, in a zipped format."""
    file_name, file_content = ifc_file_data()
    zip_file_content = None
    for i in range(2):
        in_file_name = '{:02d}_{}'.format(i, file_name)
        zip_file_content = zip_file_stream(
            in_file_name, file_content, memory_file=zip_file_content)
    return ('{}{}'.format(file_name, file_ext), zip_file_content,)


@pytest.fixture(name='ifc_multi_zip_file_data', params=['.zip'])
def ifc_multi_zip_file_data_fixture(request):
    """Fixture to return 2 IFC samples, in a zipped format."""
    return ifc_multi_zip_file_data(request.param)
