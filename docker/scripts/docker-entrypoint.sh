#!/bin/bash
set -e

# Update bemserver config file from environment variables.
# Select all env variables begin with pattern "BERSERV_" and update values in $FLASK_SETTINGS_FILE.
/scripts/update-settings.sh "BEMSRV_" ${FLASK_SETTINGS_FILE}

# Activate venv
source ${VIRTUAL_ENV}/bin/activate

# Run flask
if [ "$1" = 'flask' ] && [ "$2" = 'run' ]; then
    exec flask run --host=${FLASK_HOST} --port=${FLASK_PORT}
fi

# Execute command
exec "$@"
