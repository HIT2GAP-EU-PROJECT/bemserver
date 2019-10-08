#!/bin/bash
#===============================================================================
#
#   FILE            :  install-prod.sh
#   DESCRIPTION     :  BEMSERVER install script (production mode)
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
Usage: ./install.sh production [OPTIONS]

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
if [ -z "${BEMSERVER_DATASTORAGE_PATH}" ]; then
    error "BEMSERVER_DATASTORAGE_PATH not defined."
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

echo "Update packages list"
apt-get update > ${__STDOUT}

echo "Install packages [
    git g++ make pkg-config 
    python3-dev python-virtualenv libxmlsec1-dev
    wget unzip
    apache2 libapache2-mod-wsgi-py3
    cron
]"
apt-get install -y --no-install-recommends \
    git g++ make pkg-config \
    python3-dev libxmlsec1-dev \
    wget unzip \
    apache2 libapache2-mod-wsgi-py3 \
    cron \
    > ${__STDOUT}

apt-get install -y python-virtualenv > ${__STDOUT}    


echo "--- CREATE FOLDER STRUCTURE -----------"

# Remove application if already exist
rm -rf "${BEMSERVER_APP_PATH}"
# Create path structure
mkpath "${BEMSERVER_APP_PATH}/app"
mkpath "${BEMSERVER_APP_PATH}/scripts"
mkpath "${BEMSERVER_SETTINGS_PATH}"
mkpath "${BEMSERVER_DATASTORAGE_PATH}"
# Create tmp folder
mkpath "${__TMP}"


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
cp "${__REPOSITORY}/app/requirements.txt" "${BEMSERVER_APP_PATH}/app/requirements.txt"
pip install -r "${BEMSERVER_APP_PATH}/app/requirements.txt" > ${__STDOUT}


echo "--- INSTALL ADDITIONAL ELEMENTS ---"

echo "--- Install ifcopenshell"
wget \
    -P "${__TMP}" \
    -q "https://github.com/IfcOpenShell/IfcOpenShell/releases/download/v0.5.0-preview2/ifcopenshell-python35-master-9ad68db-linux64.zip" > ${__STDOUT}
unzip \
    -q "${__TMP}/ifcopenshell-python35-master-9ad68db-linux64.zip" \
    -d "${__TMP}" > ${__STDOUT}
mv "${__TMP}/ifcopenshell" "${VIRTUAL_ENV}/lib/python3.5/site-packages/ifcopenshell/"

echo "--- Setup datastorage"

mkpath "${BEMSERVER_DATASTORAGE_PATH}/hdf5"
chmod 770 -R "${BEMSERVER_DATASTORAGE_PATH}"
chgrp www-data -R "${BEMSERVER_DATASTORAGE_PATH}"


echo "--- COPY SOURCES ----------------------"

echo "--- Sources files"
mkpath "${BEMSERVER_APP_PATH}/app"
cp -r  \
    "${__REPOSITORY}/app/bemserver" \
    "${__REPOSITORY}/app/migrations" \
    "${__REPOSITORY}/app/.flaskenv" \
    "${__REPOSITORY}/app/application.wsgi" \
    "${BEMSERVER_APP_PATH}/app/"

echo "--- Scripts"
mkpath "${BEMSERVER_APP_PATH}/scripts"
cp -r \
    "${__REPOSITORY}/scripts/maintenance" \
    "${__REPOSITORY}/scripts/utils.sh" \
    "${BEMSERVER_APP_PATH}/scripts"

chmod 755 -R "${BEMSERVER_APP_PATH}/scripts"


echo "--- COPY SETTINGS ---------------------"

echo "--- Update bemserver configuration"
file="${__SETTINGS}/settings.cfg"
if [ -f "${__SETTINGS}/settings-prod.cfg" ]; then 
    file="${__SETTINGS}/settings-prod.cfg"
fi
cp "${file}" "${BEMSERVER_SETTINGS_PATH}/settings.cfg"

echo "--- Update wsgi configuration"
# Replace value "/path/to/venv" by ${VIRTUAL_ENV} in file
file="${BEMSERVER_APP_PATH}/app/application.wsgi"
sed -i "s#/path/to/venv#${VIRTUAL_ENV}#g" $file
    
echo "--- Update Apache configuration"
cp "${__SETTINGS}/apache2/bemserver.conf" "/etc/apache2/sites-available/bemserver.conf"
cp "${__SETTINGS}/apache2/bemserver-ssl.conf" "/etc/apache2/sites-available/bemserver-ssl.conf"
a2ensite bemserver


echo "--- CLEAN FILES -------------------"

rm -rf "${__TMP}"
rm -rf "${__REPOSITORY}"


echo ""
echo "--- INSTALLATION SUCCESS ----------"
exit 0
