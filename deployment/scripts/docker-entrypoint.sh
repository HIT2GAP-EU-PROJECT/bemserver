#!/bin/bash
set -e


# Setup file conf
/scripts/update-settings.sh "BEMSRV_" ${FLASK_SETTINGS_FILE}
/scripts/update-settings.sh "BEMTEST_" ${BEMTEST_SETTINGS_FILE}

# Activate venv
source ${BEMSRV_VENV_PATH}/bin/activate

# Run flask
if [ "$1" = 'flask' ] && [ "$2" = 'run' ]; then
    exec flask run --host=${FLASK_HOST} --port=${FLASK_PORT}
fi

# Execute command
exec "$@"
