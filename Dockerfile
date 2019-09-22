FROM debian:stretch-slim

ARG BEMSRV_APP_PATH=/app/bemserver
ARG BEMSRV_CONFIG_PATH=/app/config
ENV BEMSRV_VENV_PATH=/venv/bemserver

# Install required packages
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends git g++ make pkg-config \
    && apt-get install -y --no-install-recommends python3-dev python3-venv libxmlsec1-dev

# Setup working directory
WORKDIR ${BEMSRV_APP_PATH}/

# Copy installation files, create virtual environment, 
# install python libraries
COPY app/dev-requirements.txt app/requirements.txt ./
RUN python3 -m venv ${BEMSRV_VENV_PATH} \
    && . ${BEMSRV_VENV_PATH}/bin/activate \
    && pip install --upgrade pip \
    && pip install -r dev-requirements.txt

# Copy dependencies / application / config
COPY deployment/dependencies/ifcopenshell ${BEMSRV_VENV_PATH}/lib/python3.5/site-packages/ifcopenshell/
COPY app ./
COPY config/* ${BEMSRV_CONFIG_PATH}/

# Set required environment variables
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 \
    FLASK_SETTINGS_FILE=${BEMSRV_CONFIG_PATH}/settings.cfg \
    BEMTEST_SETTINGS_FILE=${BEMSRV_CONFIG_PATH}/tests-settings.cfg

# Copy entrypoint for container
COPY deployment/scripts /scripts/
RUN chmod +x /scripts/*

ENTRYPOINT ["/scripts/docker-entrypoint.sh"]
CMD ["flask", "run"]