"""Common tools for tests"""

import time
from io import BytesIO
import zipfile
import os
from uuid import uuid1 as uuid_gen  # noqa
from contextlib import contextmanager


# taken from http://stackoverflow.com/a/35458249
@contextmanager
def not_raises(expected_exception):
    """Check that an assertion does not raise any exception."""
    try:
        yield
    except expected_exception:
        raise AssertionError(
            'Did raise exception `{}` when it should not!'.format(
                expected_exception))
    except Exception as exc:
        raise AssertionError(
            'An unexpected exception `{}` raised.'.format(repr(exc)))


def zip_file_stream(file_name, file_content, memory_file=None):
    """Return a bytes stream of zipped data"""
    if memory_file is not None and not isinstance(memory_file, BytesIO):
        raise TypeError('Invalid memory_file, BytesIO expected.')
    if memory_file is None:
        memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'a') as zipped_file:
        data = zipfile.ZipInfo(file_name)
        data.date_time = time.gmtime(time.time())[:6]
        data.compress_type = zipfile.ZIP_DEFLATED
        zipped_file.writestr(data, file_content)
    memory_file.seek(0)
    return memory_file


def build_data_samples_path(filename):
    """Return full path for a data_samples file"""
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'data_samples',
        filename
    )


def celsius_to_fahrenheit(value, *, decimals=2):
    return round(((9. / 5.) * float(value)) + 32., decimals)


def get_dictionary_no_none(dictionary):
    """Returns a dictionary based on the input one, where all None values
    are removed
    """
    return {x: dictionary[x] for x in dictionary if dictionary[x] is not None}
