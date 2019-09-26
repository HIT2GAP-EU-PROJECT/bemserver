"""Tests for common tools"""

import datetime as dt

from bemserver.tools.common import check_list_instances

from tests import TestCoreTools


class TestToolsCommon(TestCoreTools):
    """Tests common tools"""

    def test_tools_common_check_list_instances(self):
        """Test check list instances"""

        a_list_of_datetime = [dt.datetime.now(), dt.datetime.now()]
        assert check_list_instances(a_list_of_datetime, dt.datetime)
        assert not check_list_instances(a_list_of_datetime, int)

        assert not check_list_instances('not_a_list', str)
