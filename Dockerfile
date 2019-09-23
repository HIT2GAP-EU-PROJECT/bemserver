FROM debian:stretch-slim

ARG _APP_PATH=/app/bemserver
ARG _CONFIG_PATH=/app/config
ENV VIRTUAL_ENV=/venv/bemserver

# Install required packages
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends git g++ make pkg-config \
    && apt-get install -y --no-install-recommends python3-dev python3-venv libxmlsec1-dev

# Setup working directory
WORKDIR ${_APP_PATH}/

# Copy installation files, create virtual environment, 
# install python libraries
COPY app/dev-requirements.txt app/requirements.txt ./
RUN python3 -m venv ${VIRTUAL_ENV} \
    && . ${VIRTUAL_ENV}/bin/activate \
    && pip install --upgrade pip \
    && pip install -r dev-requirements.txt

# Copy dependencies / application / config
COPY deployment/dependencies/ifcopenshell ${VIRTUAL_ENV}/lib/python3.5/site-packages/ifcopenshell/
COPY app ./
COPY config/* ${_CONFIG_PATH}/

# Set environment variables
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 \
    FLASK_SETTINGS_FILE=${_CONFIG_PATH}/settings.cfg

# Copy entrypoint for container
COPY deployment/scripts /scripts/
RUN chmod +x /scripts/*

ENTRYPOINT ["/scripts/docker-entrypoint.sh"]
CMD ["flask", "run"]