#!/bin/bash
#===============================================================================
#
#   FILE            :  bemserver.sh
#   DESCRIPTION     :  BEMSERVER commands
#   NOTES           :  root is required for some operations.
#
#   AUTHOR          :  ---
#   COMPANY         :  Nobatek/INEF4
#   CREATED         :  01/10/2019
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

__REPOSITORY=$( cd "$(dirname "$0")/.." && pwd )
__VERSION=0.1
__USAGE="
Usage: $(basename $0) [OPTIONS] COMMAND

COMMAND
    install                     Install
    setup                       Setup settings from environment variable
    maintenance                 Configure maintenance tasks

OPTIONS:
  -h, --help                    Display this message
  -v, --version                 Display version

Bemserver use environments variables and set default values if not exists:
BEMSERVER_APP_PATH              Define path to install application
BEMSERVER_SETTINGS_PATH         Define path to save application settings
BEMSERVER_DATASTORAGE_PATH      Define path to store application data
VIRTUAL_ENV                     Define path for virtual environment
"


# Imports
# ---------------

source ${__REPOSITORY}/scripts/utils.sh


# Execution
# ---------------

# Set default environment variables if not exist
if [ -z ${BEMSERVER_APP_PATH} ]; then
    export BEMSERVER_APP_PATH="/bemserver"
fi
if [ -z ${BEMSERVER_SETTINGS_PATH} ]; then
    export BEMSERVER_SETTINGS_PATH="/bemserver/settings"
fi
if [ -z ${BEMSERVER_DATASTORAGE_PATH} ]; then
    export BEMSERVER_DATASTORAGE_PATH="/bemserver/data"
fi
if [ -z ${VIRTUAL_ENV} ]; then
    export VIRTUAL_ENV="/bemserver/venv"
fi

echo "###################################"
echo "# BEMSERVER APPLICATION"
echo "###################################"


case "$1" in
    install)
        shift
        exec "${__REPOSITORY}/scripts/install/install.sh" "$@"
        ;;
    setup)
        shift
        exec "${__REPOSITORY}/scripts/setup/setup.sh" "$@"
        ;;
    maintenance)
        shift
        exec "${__REPOSITORY}/scripts/maintenance/maintenance.sh" "$@"
        ;;
    -h|--help)
        echo "${__USAGE}"
        ;;
    -v|--version)
        echo "${__VERSION}"
        ;;
    *)
        error "Bad argument [$1]"
        ;;
esac


# Ending
# ---------------

exit 0
