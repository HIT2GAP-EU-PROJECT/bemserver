"""Test API specification"""

import pytest
from apispec.utils import validate_spec

from tests import TestCoreApi


@pytest.mark.usefixtures('init_app')
class TestApiSpec(TestCoreApi):
    """API spec tests"""

    @pytest.mark.xfail(run=False)
    def test_spec_is_valid(self):
        """Test generated spec file is valid"""
        spec = self.app.extensions['flask-rest-api']['ext_obj'].spec
        assert validate_spec(spec)
