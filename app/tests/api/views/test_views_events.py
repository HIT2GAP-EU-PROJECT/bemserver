"""Tests for api events views"""

import datetime as dt
import pytest

from tests import TestCoreApi, TestCoreApiAuthCert
from tests.api.views.conftest import (
    TestingConfigAuthCertificateEnabled, generate_certificate_data)


@pytest.mark.usefixtures('init_app')
class TestApiViewsEvents(TestCoreApi):
    """Events api views tests"""

    base_uri = '/events/'

    def test_views_events(self):
        """Test get_list api endpoint"""

        # Get event list: no events
        response = self.get_items()
        assert response.status_code == 200
        assert not response.json

        # Post a new event
        event_data = {
            'execution_timestamp': dt.datetime.now().isoformat(),
            'application': 'MyApp',
            'level': 'WARNING',
            'category': 'comfort',
            'site_id': 'SiteID',
            'building_id': 'BuildingID',
            'sensor_ids': ['dev_1', 'dev_2'],
            'start_time': dt.datetime(2017, 6, 1).isoformat(),
        }
        response = self.post_item(**event_data)
        assert response.status_code == 201
        assert response.json['id'] is not None
        assert response.json['level'] == 'WARNING'
        assert response.json['sensor_ids'] == ['dev_1', 'dev_2']
        event_id = response.json['id']

        # Get event list: 1 event found
        response = self.get_items()
        assert response.status_code == 200
        assert len(response.json) == 1

        # Get event by its ID
        response = self.get_item_by_id(item_id=event_id)
        assert response.status_code == 200
        etag_value = response.headers.get('etag')

        # Post a new event
        event_data_2 = {
            'execution_timestamp': dt.datetime.now().isoformat(),
            'application': 'MyApp',
            'level': 'WARNING',
            'category': 'comfort',
            'site_id': 'SiteID',
            'building_id': 'BuildingID_2',
            'floor_id': '12',
            'sensor_ids': ['dev_3'],
            'start_time': dt.datetime(2018, 6, 1).isoformat(),
            'end_time': dt.datetime(2019, 6, 1).isoformat(),
        }
        response = self.post_item(**event_data_2)
        assert response.status_code == 201

        # Get filter by Building ID
        response = self.get_items(building_id='DummyID')
        assert response.status_code == 200
        assert not response.json
        response = self.get_items(building_id='BuildingID')
        assert response.status_code == 200
        assert len(response.json) == 1

        # Get filter by Floor ID
        response = self.get_items(floor_id='12')
        assert response.status_code == 200
        assert len(response.json) == 1

        # Get filter by sensor ID
        response = self.get_items(sensor_id='DummyID')
        assert response.status_code == 200
        assert not response.json
        response = self.get_items(sensor_id='dev_1')
        assert response.status_code == 200
        assert len(response.json) == 1

        # Get filter by date
        response = self.get_items(
            min_start_time=dt.datetime(2017, 1, 1).isoformat(),
            max_start_time=dt.datetime(2018, 1, 1).isoformat(),
        )
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['id'] == event_id
        response = self.get_items(
            max_end_time=dt.datetime(2017, 1, 1).isoformat())
        assert response.status_code == 200
        assert not response.json

        # Update event
        event_data_updated = event_data.copy()
        event_data_updated['level'] = 'ERROR'
        response = self.put_item(
            event_id, **event_data_updated,
            headers={'If-Match': etag_value})
        assert response.status_code == 200
        assert response.json['level'] == 'ERROR'
        assert response.json['sensor_ids'] == ['dev_1', 'dev_2']
        etag_value = response.headers.get('etag')

        # Update event: delete sensor IDs
        event_data_updated_again = event_data_updated.copy()
        del event_data_updated_again['sensor_ids']
        response = self.put_item(
            event_id, **event_data_updated_again,
            headers={'If-Match': etag_value})
        assert response.status_code == 200
        assert response.json['level'] == 'ERROR'
        assert response.json['sensor_ids'] == []
        etag_value = response.headers.get('etag')

        response = self.delete_item(
            item_id=event_id,
            headers={'If-Match': etag_value})
        assert response.status_code == 204

        # Test custom validators
        event_data['sensor_ids'] = ['dev_1', 'dev;2']
        response = self.post_item(**event_data)
        assert response.status_code == 422
        assert 'sensor_ids' in response.json['errors']
        del event_data['sensor_ids']
        event_data['start_time'] = dt.datetime(
            2017, 4, 11, 12, 0, 0).isoformat()
        event_data['end_time'] = dt.datetime(
            2017, 4, 11, 8, 0, 0).isoformat()
        response = self.post_item(**event_data)
        assert response.status_code == 422
        assert '_schema' in response.json['errors']


@pytest.mark.usefixtures('init_app')
class TestApiViewsEventsPermissions(TestCoreApiAuthCert):
    """Events api views tests, with authentication"""

    base_uri = '/events/'

    @pytest.mark.parametrize(
        'init_app', [TestingConfigAuthCertificateEnabled], indirect=True)
    def test_views_events_permissions(self, init_db_data):
        """Test protected api endpoint"""

        # sign in as 'bemsvrapp-cleaning-timeseries' to post events
        cert_data = generate_certificate_data('bemsvrapp-cleaning-timeseries')
        auth_header = self._auth_cert_login(cert_data)

        db_data = init_db_data
        site1_id = str(db_data['sites'][0])
        site2_id = str(db_data['sites'][1])
        site4_id = str(db_data['sites'][3])

        # Post some new events
        event_datas = [
            {
                'execution_timestamp': dt.datetime.now().isoformat(),
                'application': 'MyApp',
                'level': 'WARNING',
                'category': 'comfort',
                'site_id': site1_id,
                'building_id': 'BuildingID',
                'sensor_ids': ['dev_1', 'dev_2'],
                'start_time': dt.datetime(2017, 6, 1).isoformat(),
            },
            {
                'execution_timestamp': dt.datetime.now().isoformat(),
                'application': 'MyApp2',
                'level': 'INFO',
                'category': 'comfort',
                'site_id': 'site42',
                'building_id': 'BuildingID',
                'sensor_ids': ['dev_1', 'dev_2'],
                'start_time': dt.datetime(2017, 6, 4).isoformat(),
            },
        ]
        for event_data in event_datas:
            response = self.post_item(headers=auth_header, **event_data)
            assert response.status_code == 201

        # Get event list: 2 events found
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 2

        # sign in as 'multi-site' to get events
        cert_data = generate_certificate_data('multi-site')
        auth_header = self._auth_cert_login(cert_data)

        # Get event list: 1 event found
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 1
        # 'multi-site' permissions are 'site1' and 'site2', not 'site42'
        assert response.json[0]['site_id'] == site1_id

        # 'multi-site' can not create events
        event_data = {
            'execution_timestamp': dt.datetime.now().isoformat(),
            'application': 'MyApp999',
            'level': 'WARNING',
            'category': 'comfort',
            'site_id': 'site666',
            'building_id': 'BuildingID',
            'sensor_ids': ['dev_1', 'dev_2'],
            'start_time': dt.datetime(2017, 6, 9).isoformat(),
        }
        response = self.post_item(headers=auth_header, **event_data)
        assert response.status_code == 403
        # not allowed (permissions scope: site unauthorized)
        assert 'User has not required role' in response.json['message']

        event_data['site_id'] = site2_id
        response = self.post_item(headers=auth_header, **event_data)
        assert response.status_code == 403
        # not allowed (site authorized but not his role)
        assert 'User has not required role' in response.json['message']

        # sign in as 'app-mono-site' to get events
        cert_data = generate_certificate_data('app-mono-site')
        auth_header = self._auth_cert_login(cert_data)

        # Get event list: 0 event found
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 0

        # 'app-mono-site' can only create an event attached to 'site4'
        event_data['site_id'] = 'site666'
        response = self.post_item(headers=auth_header, **event_data)
        assert response.status_code == 403
        # not allowed (permissions scope: site unauthorized)
        assert 'User unauthorized' in response.json['message']

        event_data['site_id'] = site4_id
        response = self.post_item(headers=auth_header, **event_data)
        assert response.status_code == 201

        # Get event list: 1 event found
        response = self.get_items(headers=auth_header)
        assert response.status_code == 200
        assert len(response.json) == 1
        # 'app-mono-site' permissions are 'site4', not 'site1' or 'site42'
        assert response.json[0]['site_id'] == site4_id
