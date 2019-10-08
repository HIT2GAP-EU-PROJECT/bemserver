FROM alpine:3.10

RUN apk add --no-cache wget unzip git
RUN git clone https://github.com/HIT2GAP-EU-PROJECT/BEMOnt.git \
    && wget -q https://github.com/IfcOpenShell/IfcOpenShell/releases/download/v0.5.0-preview2/ifcopenshell-python35-master-9ad68db-linux64.zip \
    && unzip -q ifcopenshell-python35-master-9ad68db-linux64.zip


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
    && pip install -q --upgrade pip \
    && pip install -qr dev-requirements.txt

# Copy dependencies / application / config
COPY --from=0 ifcopenshell ${VIRTUAL_ENV}/lib/python3.5/site-packages/ifcopenshell/
COPY app ./
COPY settings/* ${_CONFIG_PATH}/

ENV ONTOLOGY_MODELS_PATH=/app/models
COPY --from=0 \
    BEMOnt/models/RDF/BuildingInfrastructure.rdf \
    BEMOnt/models/RDF/Property.rdf \
    BEMOnt/models/RDF/SensorRepresentation.rdf \
    BEMOnt/models/RDF/UserBehaviour.rdf \
    BEMOnt/models/RDF/Services.rdf \
    BEMOnt/models/RDF/sosa.rdf \
    BEMOnt/models/RDF/ssn.rdf \
    ${ONTOLOGY_MODELS_PATH}/

# Set environment variables
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 \
    FLASK_SETTINGS_FILE=${_CONFIG_PATH}/settings.cfg

# Copy entrypoint for container
COPY docker/scripts /scripts/
RUN chmod +x /scripts/*

ENTRYPOINT ["/scripts/docker-entrypoint.sh"]
CMD ["flask", "run"]