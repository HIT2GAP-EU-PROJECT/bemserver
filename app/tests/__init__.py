"""Tests initialization"""

import json
from urllib.parse import urljoin
from copy import deepcopy

from bemserver.database.db_mock import DatabaseMock
# from bemserver.database.ontology.manager import (
#     ontology_manager_factory)


class TestCore():
    """Parent class of all core test cases"""


class TestCoreModel(TestCore):
    """Parent class of all models test cases"""


class TestCoreDatabase(TestCore):
    """Parent class of all database test cases"""


class TestCoreDatabaseMock(TestCoreDatabase):
    """Parent class of all mocked database test cases"""

    def setup(self):
        """Setup TestCoreDatabaseMock"""
        self.db = DatabaseMock()


class TestCoreDatabaseOntology(TestCoreDatabase):
    """Parent class of all ontology database test cases"""


class TestCoreBasicServices(TestCore):
    """Parent class of all basic services test cases"""


class TestCoreExternalServices(TestCore):
    """Parent class of all external services test cases"""


class TestCoreTools(TestCore):
    """Parent class of all tools test cases"""


class TestCoreApi(TestCore):
    """Parent class of all API test cases

        Samples for subitems_uri:

            {
                'states': {
                    'uri': '/states/',
                },
                'pathologies': {
                    'uri': '/pathologies/',
                },
                'operations': {
                    'uri': '/operations/',
                },
                'operations.states': {
                    'uri': '/states/',
                },
            }
    """

    def _build_uri(self, *, uri=None, extra_uri=None):
        uri = uri or self.base_uri
        if uri is None:
            raise ValueError('uri (or base_uri) is not specified!')
        return urljoin(uri, extra_uri)

    def _build_subitem_uri(self, subitem_params):
        """
            Samples:

            subitem_params = {
                'operations': None
            }
            result is '/operations/' for operations list

            subitem_params = {
                'operations': {
                    'item_id': '2',
                }
            }
            result is '/operations/2' for operation #2

            subitem_params = {
                'operations': {
                    'item_id': '2',
                    'operations.states': None,
                }
            }
            result is '/operations/2/states' for states list of operation #2

            subitem_params = {
                'operations': {
                    'item_id': '2',
                    'operations.states': {
                        'item_id': '4',
                    }
                }
            }
            result is '/operations/2/states/4' for state #4 of operation #2
        """
        uri = None
        for k, value in subitem_params.items():
            uri = self.subitems_uri[k]['uri']
            if value is None:
                return uri
            item_id = value.pop('item_id', None)
            uri = '{}{}'.format(uri, item_id)
            if len(value.keys()) > 0:
                return '{}{}'.format(uri, self._build_subitem_uri(value))
        return uri

    def _is_json(self, content_type):
        """Indicates if this content_type is JSON or not. By default a request
        is considered to include JSON data if the mimetype is
        `application/json` or `application/*+json`.
        """
        if content_type is None:
            return False
        if (content_type.startswith('application/') and (
                content_type.endswith('/json') or
                content_type.endswith('+json'))):
            return True
        return False

    def _format_data(self, content_type, **kwargs):
        if self._is_json(content_type):
            return json.dumps(kwargs)
        return kwargs

    def _init_request(self, headers=None):
        # to prevent from keeping an old cookie from a test to another
        #  (this should not happen but...)
        self.client.delete_cookie(
            'localhost.local', self.app.session_cookie_name)
        # set the new cookie value in session
        if headers is not None:
            cookie_data = deepcopy(headers).pop('cookie', None)
            if cookie_data is not None:
                cookie_values = cookie_data.split('=')
                if (len(cookie_values) == 2 and
                        cookie_values[0] == self.app.session_cookie_name):
                    self.client.set_cookie(
                        'localhost.local', self.app.session_cookie_name,
                        cookie_values[1])

    def get_items(self, *, uri=None, extra_uri=None, **kwargs):
        """GET api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        uri = self._build_uri(uri=uri, extra_uri=extra_uri)
        return self.client.get(uri, query_string=kwargs, headers=headers)

    def get_item_by_id(self, item_id, *, uri=None, extra_uri=None, **kwargs):
        """GET api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        uri = urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id)
        return self.client.get(uri, query_string=kwargs, headers=headers)

    def post_item(self, *, uri=None, extra_uri=None, **kwargs):
        """POST api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        content_type = kwargs.pop('content_type', 'application/json')
        uri = self._build_uri(uri=uri, extra_uri=extra_uri)
        return self.client.post(
            uri, data=self._format_data(content_type, **kwargs),
            content_type=content_type, query_string=kwargs, headers=headers)

    def put_item(self, item_id, *, uri=None, extra_uri=None, **kwargs):
        """PUT api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        content_type = kwargs.pop('content_type', 'application/json')
        uri = urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id)
        return self.client.put(
            uri, data=self._format_data(content_type, **kwargs),
            content_type=content_type, query_string=kwargs, headers=headers)

    def patch_item(self, item_id, *, uri=None, extra_uri=None, **kwargs):
        """PATCH api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        content_type = kwargs.pop('content_type', 'application/json')
        uri = urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id)
        return self.client.patch(
            uri, data=self._format_data(content_type, **kwargs),
            content_type=content_type, query_string=kwargs, headers=headers)

    def delete_item(self, item_id, *, uri=None, extra_uri=None, **kwargs):
        """DELETE api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        uri = urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id)
        return self.client.delete(uri, query_string=kwargs, headers=headers)

    def search_items(self, *, uri=None, extra_uri=None, **kwargs):
        """GET api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        uri = urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), 'search')
        return self.client.get(uri, query_string=kwargs, headers=headers)

    def get_subitems(self, item_id, subitem_params, *, uri=None,
                     extra_uri=None, **kwargs):
        """GET api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        uri = '{}{}'.format(
            urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id),
            self._build_subitem_uri(subitem_params))
        return self.client.get(uri, query_string=kwargs, headers=headers)

    def get_subitem_by_id(self, item_id, subitem_params, *, uri=None,
                          extra_uri=None, **kwargs):
        """GET api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        uri = '{}{}'.format(
            urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id),
            self._build_subitem_uri(subitem_params))
        return self.client.get(uri, query_string=kwargs, headers=headers)

    def post_subitem(self, item_id, subitem_params, *, uri=None,
                     extra_uri=None, **kwargs):
        """POST api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        content_type = kwargs.pop('content_type', 'application/json')
        uri = '{}{}'.format(
            urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id),
            self._build_subitem_uri(subitem_params))
        data = json.dumps(kwargs) if '/json' in content_type else kwargs
        return self.client.post(
            uri, data=data, content_type=content_type, query_string=kwargs,
            headers=headers)

    def put_subitem(self, item_id, subitem_params, *, uri=None,
                    extra_uri=None, **kwargs):
        """PUT api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        content_type = kwargs.pop('content_type', 'application/json')
        uri = '{}{}'.format(
            urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id),
            self._build_subitem_uri(subitem_params))
        data = json.dumps(kwargs) if '/json' in content_type else kwargs
        return self.client.put(
            uri, data=data, content_type=content_type, query_string=kwargs,
            headers=headers)

    def patch_subitem(self, item_id, subitem_params, *, uri=None,
                      extra_uri=None, **kwargs):
        """PATCH api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        content_type = kwargs.pop('content_type', 'application/json')
        uri = '{}{}'.format(
            urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id),
            self._build_subitem_uri(subitem_params))
        data = json.dumps(kwargs) if '/json' in content_type else kwargs
        return self.client.patch(
            uri, data=data, content_type=content_type, query_string=kwargs,
            headers=headers)

    def delete_subitem(self, item_id, subitem_params, *, uri=None,
                       extra_uri=None, **kwargs):
        """DELETE api call"""
        headers = kwargs.pop('headers', None)
        self._init_request(headers)
        uri = '{}{}'.format(
            urljoin(self._build_uri(uri=uri, extra_uri=extra_uri), item_id),
            self._build_subitem_uri(subitem_params))
        return self.client.delete(uri, query_string=kwargs, headers=headers)


class TestCoreApiAuthCert(TestCoreApi):

    def _auth_cert_login(self, cert_data):
        headers = {'SSL_CLIENT_S_DN': cert_data}
        response = self.post_item(
            uri='/auth/', extra_uri='cert', headers=headers)
        assert response.status_code == 200
        # return authentication cookie header
        for set_cookie_part in response.headers['set-cookie'].split(';'):
            if '{}='.format(self.app.session_cookie_name) in set_cookie_part:
                return {'cookie': set_cookie_part.strip()}
        return {}

    def _get_uacc(self, db_data, uid):
        for cur_uacc in db_data['users']:
            if cur_uacc.uid == uid:
                return cur_uacc
        return None
