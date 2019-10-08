#!/bin/bash
#===============================================================================
#
#   FILE            :  maintenance.sh
#   DESCRIPTION     :  BEMSERVER maintenance commands
#   NOTES           :  ---
#
#   AUTHOR          :  ---
#   COMPANY         :  Nobatek/INEF4
#   CREATED         :  02/10/2019
#
#   VERSION         :  0.1
#
#===============================================================================
#   REVISION        :  ---
#   SUBJECT         :  ---
#   DESCRIPTION     :  ---
#
#   DATE            :  ---
#===============================================================================

set -e

# Initialization
# ---------------

__USAGE="
Usage: $(basename $0) CMD [OPTIONS]

CMD                             Command to execute
    activate                     - Create cron task for auto maintenance
    deactivate                   - Remove cron auto maintenance task
    run                          - Run maintenance manualy

OPTIONS:
    -h, --help                  Display this message.

Maintenance use environments variables:
BEMSERVER_SETTINGS_PATH         Define path to save application settings
BEMSERVER_DATASTORAGE_PATH      Define path to store application data
"

__REPOSITORY=$( cd "$(dirname "$0")/../.." && pwd )


# Imports
# ---------------

source ${__REPOSITORY}/scripts/utils.sh


# Read arguments
# ---------------

set +e
while [ -n "$1" ]; do
    case "$1" in
        activate|deactivate|run)
            ACTION="$1"
            ;;
        -h|--help)
            echo "${__USAGE}"
            exit 0
            ;;
        *)
            error "Bad argument [$1]"
            ;;
    esac
    shift
done
set -e



# Check arguments
# ---------------

if [ -z "${ACTION}" ]; then
    error "ACTION not found"
fi

if [ -z "${BEMSERVER_SETTINGS_PATH}" ]; then
    error "BEMSERVER_SETTINGS_PATH not defined"
fi
if [ -z "${BEMSERVER_DATASTORAGE_PATH}" ]; then
    error "BEMSERVER_DATASTORAGE_PATH not defined."
fi

if [ ! -d "${BEMSERVER_SETTINGS_PATH}" ]; then
    error "Directory not found [${BEMSERVER_SETTINGS_PATH}]"
fi
if [ ! -d "${BEMSERVER_DATASTORAGE_PATH}" ]; then
    error "Directory not found [${BEMSERVER_DATASTORAGE_PATH}]"
fi


# Execute actions
# ---------------

echo "--- MAINTENANCE -----------------------"

COMMAND="${__REPOSITORY}/scripts/maintenance/repack_hdf5.sh"
CRON_STRING="0 12 * * 0 ${COMMAND}"

case "${ACTION}" in
    activate)
        CTAB=$(crontab -l 2>/dev/null)
        if grep -Fxq "${CRON_STRING}" <<< ${CTAB}
        then
            echo "Task already exist..."
        else
            echo "Add task..."
            (echo ${CTAB}; echo "${CRON_STRING}") | crontab -
        fi
        ;;
    deactivate)
        echo "Delete task..."
        crontab -l | grep -Fv "${CRON_STRING}" | crontab -
        ;;
    run)
        echo "Running..."
        exec ${COMMAND}
        ;;
esac

echo "--- MAINTENANCE SUCCESS ---------------"
exit 0
