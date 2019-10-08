#!/bin/bash
#===============================================================================
#
#   FILE            :  install-dev.sh
#   DESCRIPTION     :  BEMSERVER install script (development mode)
#   NOTES           :  root is required for some operations.
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

__USAGE="
Usage: ./install.sh development [OPTIONS]

OPTIONS:
    -s, --settings              Settings folder to use for installation.
    -h, --help                  Display this message.
    -q, --quiet                 Use quiet mode.
"

__STDOUT="/dev/stdout"
__STDERR="/dev/stderr"
__REPOSITORY=$( cd "$(dirname "$0")/../.." && pwd )

__TMP="/tmp/bemserver"
__SETTINGS="${__REPOSITORY}/settings"


# Imports
# ---------------

source ${__REPOSITORY}/scripts/utils.sh


# Read arguments
# ---------------

set +e
while [ -n "$1" ]; do
    case "$1" in
        -s|--settings)
            shift
            __SETTINGS=$1
        ;;
        -q|--quiet)
            __STDOUT="/dev/null"
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

if [ -z "${BEMSERVER_APP_PATH}" ]; then
    error "BEMSERVER_APP_PATH not defined."
fi
if [ -z "${BEMSERVER_SETTINGS_PATH}" ]; then
    error "BEMSERVER_SETTINGS_PATH not defined"
fi
if [ -z "${VIRTUAL_ENV}" ]; then
    error "VIRTUAL_ENV not defined"
fi

if [ "${__REPOSITORY}" == "${BEMSERVER_APP_PATH}" ]; then
    error "Bad installation folder."
fi
if [ ! -d "${__SETTINGS}" ]; then
    error "__SETTINGS is not a folder"
fi


# Execute actions
# ---------------


echo "--- INSTALL PACKAGES ------------------"

echo "Update/Upgrade current packages"
apt-get update > ${__STDOUT}
apt-get upgrade -y > ${__STDOUT}
echo "Install compile packages (g++, make, pkg-config...)"
apt-get install -y --no-install-recommends git g++ make pkg-config > ${__STDOUT}
echo "Install python packages"
apt-get install -y python-virtualenv > ${__STDOUT}
apt-get install -y --no-install-recommends python3-dev libxmlsec1-dev > ${__STDOUT}
echo "Install wget unzip"
apt-get install -y --no-install-recommends wget unzip > ${__STDOUT}


echo "--- CREATE FOLDER STRUCTURE -----------"

# Remove application if already exist
rm -rf "${BEMSERVER_APP_PATH}"
# Create path structure
mkpath "${BEMSERVER_APP_PATH}/app"
mkpath "${BEMSERVER_APP_PATH}/scripts"
mkpath "${BEMSERVER_SETTINGS_PATH}"
# Create tmp folder
mkpath "${__TMP_DIR}"


echo "--- INSTALL VENV ------------------"

# Remove environment if already exist
rm -rf "${VIRTUAL_ENV}"
mkpath "${VIRTUAL_ENV}"

echo "Create virtual environment"
virtualenv -p python3 "${VIRTUAL_ENV}"
source "${VIRTUAL_ENV}/bin/activate"
echo "Upgrade pip utility"
pip install --upgrade pip > ${__STDOUT}
echo "pip install requirements" 
cp \
    "${__REPOSITORY}/app/requirements.txt" \
    "${__REPOSITORY}/app/dev-requirements.txt" \
    "${BEMSERVER_APP_PATH}/app/"
pip install -r "${BEMSERVER_APP_PATH}/app/dev-requirements.txt" > ${__STDOUT}


echo "--- INSTALL ADDITIONAL ELEMENTS ---"

echo "--- Install ifcopenshell"
wget \
    -P "${__TMP_DIR}" \
    -q "https://github.com/IfcOpenShell/IfcOpenShell/releases/download/v0.5.0-preview2/ifcopenshell-python35-master-9ad68db-linux64.zip" > ${__STDOUT}
unzip \
    -q "${__TMP_DIR}/ifcopenshell-python35-master-9ad68db-linux64.zip" \
    -d "${__TMP_DIR}" > ${__STDOUT}
mv "${__TMP_DIR}/ifcopenshell" "${VIRTUAL_ENV}/lib/python3.5/site-packages/ifcopenshell/"

echo "--- Install ontology"
mkpath "${BEMSERVER_DATASTORAGE_PATH}/ontology"
git clone --depth 1 https://github.com/HIT2GAP-EU-PROJECT/BEMOnt.git "${__TMP_DIR}/bemont/" > ${__STDOUT}
mv \
    "${__TMP_DIR}/bemont/models/RDF/BuildingInfrastructure.rdf" \
    "${__TMP_DIR}/bemont/models/RDF/Property.rdf" \
    "${__TMP_DIR}/bemont/models/RDF/SensorRepresentation.rdf" \
    "${__TMP_DIR}/bemont/models/RDF/UserBehaviour.rdf" \
    "${__TMP_DIR}/bemont/models/RDF/Services.rdf" \
    "${__TMP_DIR}/bemont/models/RDF/sosa.rdf" \
    "${__TMP_DIR}/bemont/models/RDF/ssn.rdf" \
    "${BEMSERVER_DATASTORAGE_PATH}/ontology/"


echo "--- COPY SOURCES ----------------------"

echo "--- Sources files"
mkdir "${BEMSERVER_APP_PATH}/app"
cp -r "${__REPOSITORY}/app/" "${BEMSERVER_APP_PATH}/app/"

echo "--- Scripts"
mkdir "${BEMSERVER_APP_PATH}/scripts"
cp -r \
    "${__REPOSITORY}/scripts/maintenance" \
    "${__REPOSITORY}/scripts/utils.sh" \
    "${BEMSERVER_APP_PATH}/scripts"

chmod 755 -R "${BEMSERVER_APP_PATH}/scripts"


echo "--- COPY SETTINGS ---------------------"

echo "--- Update bemserver configuration"
file="${__SETTINGS}/settings.cfg"
if [ -f "${__SETTINGS}/settings-dev.cfg" ]; then 
    file="${__SETTINGS}/settings-dev.cfg"
fi
cp "${file}" "${BEMSERVER_SETTINGS_PATH}/settings.cfg"


echo "--- CLEAN FILES -------------------"

rm -rf "${__TMP_DIR}"
rm -rf "${__REPOSITORY}"


echo ""
echo "--- INSTALLATION SUCCESS ----------"
exit 0
