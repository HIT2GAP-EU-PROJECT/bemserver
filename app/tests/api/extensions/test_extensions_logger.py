"""Tests for api building views"""

from unittest import mock
from flask import Flask

from bemserver.api.extensions.logger import init_app

from tests import TestCoreApi
from tests.api.views.conftest import TestingConfig


class TestingConfigLoggerTests(TestingConfig):
    PROPAGATE_EXCEPTIONS = False


class TestApiExtensionsTestLogger(TestCoreApi):

    def test_logger(self, tmpdir):

        app = Flask('Test app')
        TestingConfigLoggerTests.LOGGER_DIR = str(tmpdir)
        app.config.from_object(TestingConfigLoggerTests)
        init_app(app)

        logger = app.logger
        logger.debug = mock.MagicMock(name='debug')
        logger.info = mock.MagicMock(name='info')
        logger.error = mock.MagicMock(name='error')
        logger.warning = mock.MagicMock(name='warning')
        logger.critical = mock.MagicMock(name='critical')

        my_exc = ValueError("Wrong value")

        @app.route('/uncaught_exc')
        def test_uncaught_exc():
            raise my_exc

        # Uncaught exception is logged
        app.test_client().get('/uncaught_exc')
        assert not logger.debug.called
        assert not logger.info.called
        assert not logger.warning.called
        assert not logger.critical.called
        assert logger.error.called
        _, exc_info_dict = logger.error.call_args
        exc_info = exc_info_dict['exc_info']
        _, exc_value, _ = exc_info
        assert exc_value == my_exc
        logger.error.reset_mock()

        # Client error is not logged
        app.test_client().get('/wrong_path')
        assert not logger.debug.called
        assert not logger.info.called
        assert not logger.warning.called
        assert not logger.error.called
        assert not logger.critical.called
