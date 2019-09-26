"""APISpec documentation responses."""

import copy

from .schemas import ErrorSchema


_RESPONSES = {
    200: {'description': 'successful operation'},
    201: {'description': 'successful operation'},
    204: {'description': 'successful operation'},
    302: {'description': 'redirection'},
    400: {'description': 'invalid request'},
    401: {'description': 'authentication required'},
    403: {'description': 'access refused'},
    404: {'description': 'item not found'},
    413: {'description': 'request too large'},
    422: {'description': 'invalid input'},
    500: {'description': 'internal server error'},
}


def build_responses(status_codes, *, schemas=None):
    """Return information about possible status code responses.

    :param list|tuple status_codes:
        List of possible status codes (each as integer).
        If None, default is [200, 500].
    :param dict schemas:
        Composition of status codes and marshmallow.Schema response schemas.
        Example: {200: ResponseSchema, 401: CustomSchema}
    :return dict: Status code responses for APISpec documentation.
    """
    # set default statuses if None defined
    if status_codes is None or not isinstance(status_codes, (list, tuple,)):
        status_codes = [200, 500]

    # get responses information for status_codes
    responses = {}
    for status_code in status_codes:
        try:
            status_code = int(status_code)  # int expected
            resp = copy.deepcopy(
                _RESPONSES.get(status_code, {'description': ''}))
            if 400 <= status_code < 500:
                resp['schema'] = ErrorSchema
            if schemas is not None and status_code in schemas:
                resp['schema'] = schemas[status_code]
            responses[status_code] = resp
        except ValueError:
            # maybe status_code could not be parsed to int
            pass

    return responses
