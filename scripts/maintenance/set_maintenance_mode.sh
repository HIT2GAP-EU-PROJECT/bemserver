#!/bin/sh

BASE_PATH=/srv/prj/hit2gap/bemserver/
SETTINGS_FILE=${BASE_PATH}application/settings.cfg

# Put application in maintenance mode
echo $(date) "Putting application in maintenance mode..."
echo "MAINTENANCE_MODE=True" >> $SETTINGS_FILE
systemctl reload apache2
echo $(date) "Apache reloaded"
