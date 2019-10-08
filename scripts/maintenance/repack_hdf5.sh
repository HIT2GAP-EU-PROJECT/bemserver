#!/bin/sh


# Imports
# ---------------

__REPOSITORY=$( cd "$(dirname "$0")/../.." && pwd )
. ${__REPOSITORY}/scripts/utils.sh


# Check arguments
# ---------------

if [ -z "${BEMSERVER_SETTINGS_PATH}" ]; then
    error "BEMSERVER_SETTINGS_PATH not defined"
fi
if [ -z "${BEMSERVER_DATASTORAGE_PATH}" ]; then
    error "BEMSERVER_DATASTORAGE_PATH not defined."
fi


# Execute
# ---------------

REPACK_SCRIPT=${BEMSERVER_REPOSITORY_PATH}/scripts/maintenance/repack_hdf5.py

SETTINGS_FILE=${BEMSERVER_SETTINGS_PATH}/settings.cfg
HDF5_DIR_PATH=${BEMSERVER_DATASTORAGE_PATH}/hdf5
LOCK_FILE=${BEMSERVER_DATASTORAGE_PATH}/HDF5_LOCK


# Check database lock
if [ -f "$LOCK_FILE" ]; then
    echo $(date) "HDF5 database locked, exiting repack script"
    exit 1
fi

echo $(date) "Launching HDF5 database repack"

# Lock database
touch "$LOCK_FILE"

# Backup config file
cp $SETTINGS_FILE ${SETTINGS_FILE}.bak

# Put application in maintenance mode
echo $(date) "Putting application in maintenance mode..."
echo "MAINTENANCE_MODE=True" >> $SETTINGS_FILE
service apache2 reload
echo $(date) "Apache reloaded"

# Repack
# Redirect stderr to stdout and filter out NaturalNameWarning
echo $(date) "Repack..."
$REPACK_SCRIPT 2>&1 | grep -v NaturalNameWarning
echo $(date) "Repack done"

# Give ownership of repacked files to apache
echo $(date) "Setting file ownership"
chown -R www-data:www-data $HDF5_DIR_PATH

# Restore config file and reload config
echo $(date) "Restore application configuration"
mv ${SETTINGS_FILE}.bak $SETTINGS_FILE
chown www-data:www-data $SETTINGS_FILE
chmod 640 $SETTINGS_FILE
service apache2 reload
echo $(date) "Apache reloaded"

# Release database lock
rm "$LOCK_FILE"

echo $(date) "HDF5 database repack done"
