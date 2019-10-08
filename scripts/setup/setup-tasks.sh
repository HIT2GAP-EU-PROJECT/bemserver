#!/bin/bash

#===============================================================================
# SETUP TASKS
#===============================================================================

__REPOSITORY=$( cd "$(dirname "$0")/../.." && pwd )


# Imports
# ---------------

source ${__REPOSITORY}/scripts/utils.sh


# Check environment variables
# ---------------------------

if [ -z "${BEMSERVER_SETTINGS_PATH}" ]; then
    error "BEMSERVER_SETTINGS_PATH not defined"
fi


# Function definitions
# --------------------

function setup_bemserver_conf()
# Usage: setup_bemserver_conf PATTERN
# Update bemserver settings file from environment variables

# PATTERN                         PATTERN to use to detect wich environment variable to use for update.
{
    echo "--- SETUP BEMSERVER SETTINGS -----"
    file="${BEMSERVER_SETTINGS_PATH}/settings.cfg"
    if [ ! -f "${file}" ]; then
        error "File not found [${file}]"
    fi

    cutval=$((${#1}+1))

    echo "Updating $file"
    if [ -n ${ONTOLOGY_BASE_URL} ]; then
        setup_conf "${file}" "ONTOLOGY_BASE_URL" "${ONTOLOGY_BASE_URL}"
    fi

    printenv | grep ^"${1}" | cut -c ${cutval}- | while read -r line ; do
        IFS="=" read -ra parts <<< "$line"
        setup_conf "${file}" "${parts[0]}" "${parts[1]}"
    done
}

function setup_conf()
# Usage: setup_conf FILE KEY VALUE
# Update KEY=VALUE parameter in FILE. If KEY exist update VALUE, else add KEY='VALUE' entry.

# FILE                            FILE to update
# KEY                             KEY of parameter to update
# VALUE                           VALUE of parameter to update
{
    regexp="^$2\s?=.*"
    new="$2='$3'"
    if [ -z $(grep -E "$regexp" $1) ]
    then
        echo "${new}" >> $1
    else
        sed -i -E "s#$regexp#${new}#g" $1
    fi
}
