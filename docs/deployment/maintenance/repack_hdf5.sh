#!/bin/sh

BASE_PATH=/srv/prj/hit2gap/bemserver/
SETTINGS_FILE=${BASE_PATH}application/settings.cfg
HDF5_DIR_PATH=${BASE_PATH}hdf5

REPACK_SCRIPT=${BASE_PATH}repack_hdf5.py

LOCK_FILE=${BASE_PATH}HDF5_LOCK


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
systemctl reload apache2
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
systemctl reload apache2
echo $(date) "Apache reloaded"

# Release database lock
rm "$LOCK_FILE"

echo $(date) "HDF5 database repack done"
