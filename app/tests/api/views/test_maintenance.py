"""Tests for api building views"""

from pathlib import Path
import pytest

from bemserver.api import create_app

from tests import TestCoreApi
from tests.api.views.conftest import TestingConfig


HTTP_METHODS = (
    'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'TRACE')


class TestApiExtensionsTestMaintenance(TestCoreApi):

    @pytest.mark.parametrize('method', HTTP_METHODS)
    def test_maintenance_mode(self, method, tmpdir):

        # Logging temp dir
        # Cast to Path (https://github.com/pytest-dev/pytest/issues/1260)
        log_dir = Path(str(tmpdir)) / 'log'
        log_dir.mkdir()

        class Config(TestingConfig):
            MAINTENANCE_MODE = True
            LOGGER_DIR = log_dir

        app = create_app(config_class=Config)
        response = app.test_client().open('/', method=method)
        assert response.status_code == 503
        response = app.test_client().open('/whatever', method=method)
        assert response.status_code == 503
