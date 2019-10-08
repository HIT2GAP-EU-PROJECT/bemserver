#!/bin/bash

#===============================================================================
# TOOLS
#===============================================================================

function mkpath()
# Usage: mkpath /my/new/directory
# Create path to directory if not exist
{
    while [ -n "$1" ]; do
        if [ ! -d "$1" ];then
            mkp_parent=$(dirname "$1")
            if [ -d "$mkp_parent" ];then
                mkdir $1
            else
                mkpath "$mkp_parent"
                mkdir $1
            fi
        fi
        shift
    done
}

function warn()
# Usage: warn MESSAGE
{
    echo ""
    echo "WARNING: $1"
}

function error()
# Usage: error MESSAGE
{
    echo ""
    echo "Stopped. See -h, --help for more help."
    echo "ERROR: $1"
    exit 1
}