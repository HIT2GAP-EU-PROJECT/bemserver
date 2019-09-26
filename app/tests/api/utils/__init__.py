"""Utils for api tests"""

from io import BytesIO

from .api_response import JSONResponse  # noqa


def build_file_obj(file_name, file_content):
    """Return a file object"""
    if not isinstance(file_content, BytesIO):
        file_content = BytesIO(bytes(file_content, 'utf-8'))
    return (file_content, file_name)
