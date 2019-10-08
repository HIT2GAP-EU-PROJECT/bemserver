#!/bin/bash
#===============================================================================
#
#   FILE            :  setup.sh
#   DESCRIPTION     :  BEMSERVER set setup command
#   NOTES           :  ---
#
#   AUTHOR          :  ---
#   COMPANY         :  Nobatek/INEF4
#   CREATED         :  02/10/2019
#
#   VERSION         :  0.1
#
#===============================================================================

set -e

# Initialization
# ---------------

__REPOSITORY=$( cd "$(dirname "$0")/../.." && pwd )
__USAGE="
Usage: $(basename $0) [OPTIONS]

OPTIONS
    -h, --help                  Display this message

Setup use environments variables:
BEMSERVER_SETTINGS_PATH         Define path to save application settings
"


# Imports
# ---------------

source ${__REPOSITORY}/scripts/utils.sh
source ${__REPOSITORY}/scripts/setup/setup-tasks.sh


# Read arguments
# ---------------

set +e
while [ -n "$1" ]; do
    case "$1" in
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


# Execute actions
# ---------------

setup_bemserver_conf "BEMSERV_"

echo ""
echo "--- UPDATE SETTINGS SUCCESS -------"
exit 0
