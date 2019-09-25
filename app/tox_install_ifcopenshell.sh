#!/bin/sh

# IfcOpenShell library is not packaged on Pypi and must be installed manually.
# I'd rather not do this in the installation procedure but for tests, it'll do.

ENV=$1
SITE_PACKAGES=$2

if [ ! -d "$SITE_PACKAGES/ifcopenshell" ]; then

  echo "Installing ifcopenshell..."

  if [ `uname -m` = x86_64 ]; then
    ARCHI=64
  else
    ARCHI=32
  fi

  ENV_NUM=`echo $ENV | cut -c3-4`

  IFCOPENSHELL_FILE="ifcopenshell-python"$ENV_NUM"-master-9ad68db-linux"$ARCHI".zip"
  IFCOPENSHELL_URL="https://github.com/IfcOpenShell/IfcOpenShell/releases/download/v0.5.0-preview2/"$IFCOPENSHELL_FILE
  
  temp_dir=$(mktemp -d)
  cd $temp_dir
  wget $IFCOPENSHELL_URL
  unzip $IFCOPENSHELL_FILE
  mv ifcopenshell $SITE_PACKAGES
  rm -R ${temp_dir}

  echo "Done installing ifcopenshell..."
fi
