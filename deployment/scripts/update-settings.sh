#!/bin/bash
set -e

# Update settings files from environment variables.
# Get environment variables beginning with PATTERN and update or create values in CONFIG_FILE
# Usage: ./update-settings.sh "BEMSRV_" "/config/settings.cfg"
#

CONFIG_FILE=$2
PATTERN="$1"
CUTVAL=$((${#PATTERN}+1))

# Update key, value parameters in CONFIG_FILE.
# If key exist update value, if not create key=value pair.
function update_file(){
    regexp="^$1=\(.*\)"
    if [ -z $(grep "$regexp" $CONFIG_FILE) ]
    then
        echo "$1 = '$2'" >> $CONFIG_FILE
    else
        sed -i "s#$regexp#$1 = '$2'#g" $CONFIG_FILE
    fi
}

echo "-----------------------------------"
echo "Updating BEMSERVER settings ($CONFIG_FILE)"

printenv | grep ^"${PATTERN}" | cut -c ${CUTVAL}- | while read -r line ; do
    IFS="=" read -ra parts <<< "$line"
    update_file "${parts[0]}" "${parts[1]}"
done

echo "Update success"
echo "-----------------------------------"