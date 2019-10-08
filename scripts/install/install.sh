#!/bin/bash
#===============================================================================
#
#   FILE            :  install.sh
#   DESCRIPTION     :  BEMSERVER install commands
#   NOTES           :  root is required for some operations.
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
Usage: $(basename $0) TYPE [OPTIONS]

TYPE                            Type of installation to perform
    development                  - development install with tests
    production                   - production install (ssh not activated by default)

OPTIONS:
    -h, --help                  Display this message.

Installation use environments variables:
BEMSERVER_APP_PATH              Define path to install application
BEMSERVER_SETTINGS_PATH         Define path to save application settings
BEMSERVER_DATASTORAGE_PATH      Define path to store application data
VIRTUAL_ENV                     Define path for virtual environment
"

__REPOSITORY=$( cd "$(dirname "$0")/../.." && pwd )


# Imports
# ---------------

source ${__REPOSITORY}/scripts/utils.sh


# Read arguments
# ---------------

case "$1" in
    development|production)
        TYPE="$1"
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


# Check arguments
# ---------------

if [ -z "${TYPE}" ]; then
    error "TYPE not found"
fi


# Execute actions
# ---------------


case "${TYPE}" in
    development)
        exec "${__REPOSITORY}/scripts/install/install-dev.sh" "$@"
        ;;
    production)
        exec "${__REPOSITORY}/scripts/install/install-prod.sh" "$@"
        ;;
esac


echo ""
echo "--- INSTALLATION SUCCESS ----------"
exit 0
