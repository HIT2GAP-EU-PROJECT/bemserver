#!/usr/bin/env python3
"""Sample wsgi file

Customize path to virtual environment and you're done
"""

import os
import sys
import runpy

# pylint: disable=wrong-import-position
# pylint: disable=invalid-name

# Working with Virtual Environment
# see http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# and also https://gist.github.com/LeZuse/4032238
# and http://stackoverflow.com/questions/436198/
runpy.run_path('/path/to/venv/bin/activate_this.py')

# Add application to Python path
# Check before adding so as not to add it multiple times
# when reloading the file:
# https://code.google.com/p/modwsgi/wiki/ReloadingSourceCode
PATH = os.path.dirname(__file__)
if PATH not in sys.path:
    sys.path.append(PATH)

# Set environment variable to indicate production mode
os.environ['FLASK_ENV'] = 'production'

# Provide path to custom settings file
os.environ['FLASK_SETTINGS_FILE'] = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'settings.cfg'
)

# Unleash the beast
from bemserver.api import create_app  # noqa
application = create_app()
