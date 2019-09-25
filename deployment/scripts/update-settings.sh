#!/bin/bash
set -e

# Update settings files from environment variables.
# Get environment variables beginning with PATTERN and update or create values in CONFIG_FILE
# Usage: /scripts/update-settings.sh "BEMSRV_" "${FLASK_SETTINGS_FILE}"
#

CONFIG_FILE=$2
PATTERN="$1"
CUTVAL=$((${#PATTERN}+1))

# Update key, value parameters in CONFIG_FILE.
# If key exist update value, if not create key=value pair.
function update_file(){
    regexp="^$1\s?=.*"
    # echo "PATTERN: $regexp"
    if [ -z $(grep -E "$regexp" $CONFIG_FILE) ]
    then
        # echo "NEW VALUE: $1='$2'"
        echo "$1='$2'" >> $CONFIG_FILE
    else
        # echo "UPDATE: $1='$2'"
        sed -i -E "s#$regexp#$1='$2'#g" $CONFIG_FILE
    fi
}

echo "-----------------------------------"
echo "Updating BEMSERVER settings ($CONFIG_FILE)"

printenv | grep ^"${PATTERN}" | cut -c ${CUTVAL}- | while read -r line ; do
    IFS="=" read -ra parts <<< "$line"
    update_file "${parts[0]}" "${parts[1]}"
done

# Specific treatment for ONTOLOGY_BASE_URL
if [ ! -z ${ONTOLOGY_BASE_URL} ]; then
    update_file "ONTOLOGY_BASE_URL" "${ONTOLOGY_BASE_URL}"
fi

echo "Update success"
echo "-----------------------------------"