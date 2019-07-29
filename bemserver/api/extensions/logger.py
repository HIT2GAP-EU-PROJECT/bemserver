"""Application logger"""

import time
import re
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import request
from flask.logging import default_handler


class RequestFormatter(logging.Formatter):
    """Custom log Formatter injecting request information

    http://flask.pocoo.org/docs/1.0/logging/#injecting-request-information
    """
    def format(self, record):
        if request:
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
        else:
            record.url = ''
            record.method = ''
            record.remote_addr = ''
        return super().format(record)


def init_app(app):

    # Use default config in DEBUG mode, configure logger otherwise
    if not app.debug:

        log_dir = Path(app.config['LOGGER_DIR'])
        log_level = app.config['LOGGER_LEVEL']
        log_backup_count = app.config['LOGGER_BACKUP']
        log_format = app.config['LOGGER_FORMAT']

        # Create a daily rotated log file handler
        # See example: http://stackoverflow.com/a/25387192
        file_handler = TimedRotatingFileHandler(
            str(log_dir / 'bemserver.log'),
            when='midnight',
            backupCount=log_backup_count, utc=True)
        file_handler.suffix = '%Y-%m-%d'
        file_handler.extMatch = re.compile(r'^\d{4}-\d{2}-\d{2}$')

        # Create record formatter
        formatter = RequestFormatter(log_format)
        formatter.converter = time.gmtime
        file_handler.setFormatter(formatter)

        # Remove Flask default handler
        app.logger.removeHandler(default_handler)

        # Add our custom handler to all loggers
        for logger in (
                app.logger,
                logging.getLogger('bemserver'),
                # Don't handle werkzeug logging (too verbose)
                # logging.getLogger('werkzeug'),
                # Insert logger from libraries
                # logging.getLogger('some_library'),
        ):
            # Set log severity level at logger level
            # By default, the Handler is configured with 'NOTSET', which means
            # process all messages that loggers pass down.
            logger.setLevel(log_level)
            logger.addHandler(file_handler)
