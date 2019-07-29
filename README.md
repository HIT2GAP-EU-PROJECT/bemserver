Installation
============

### Install and configure dependencies

### Install core itself

.. code-block:: shell

    # Create virtual environment
    $ virtualenv -p /usr/bin/python3 $VIRTUALENVS_DIR/bemserver

    # Activate virtualenv
    $ source $VIRTUALENVS_DIR/bemserver/bin/activate

    # Install python header files and development stuff
    # (libxmlsec1-dev is required by python3-saml)
    $ aptitude install g++ make python3-dev libxmlsec1-dev

    # Install
    pip install -r requirements.txt
    # an upgrade of pip can be required (for example scipy dependancy requires it)
    python -m pip install --upgrade pip


### Install IfcOpenShell

    IfcOpenShell has to be installed manually.

    Download IfcOpenShell-python archive from the official site:

        http://ifcopenshell.org/python.html

    (acceptable version >= 0.5.0 preview 2)

    Place the extracted archive in the site-packages folder of the virtualenv:

        $VIRTUALENVS_DIR/bemserver/lib/python3.5/site-packages/


### Install Jena / Fuseki

    Jena / Fuseki is distributed as a docker container:

        https://hub.docker.com/r/stain/jena-fuseki/

.. code-block:: shell

    # Create persistent storage volume container first
    $ docker run --name fuseki-data -v /fuseki busybox

    # Create jena/fuseki container using that volume
    $ docker run -d --name fuseki -p 3030:3030 \
      --volumes-from fuseki-data \
      -e ADMIN_PASSWORD=pickasupersecurepassword \
      -e JVM_ARGS=-Xmx2048M \
      --log-opt max-size=10m --log-opt max-file=3 \
      --restart unless-stopped \
      stain/jena-fuseki

    # On subsequent runs, just use
    $ docker restart fuseki


    To manage the ontology, browse http://localhost:3030/

    Create a new dataset called "hit2gap"

    Clone ontology repo

.. code-block:: shell

    $ git clone https://github.com/HIT2GAP-EU-PROJECT/BEMOnt

    From the web interface, select the new "hit2gap" dataset and upload files.
    Load following files from ontology repo:

    - BuildingInfrastructure.rdf
    - Property.rdf
    - SensorRepresentation.rdf
      UserBehaviour.rdf
      sosa.owl
      ssn.owl

### TODO: describe configuration to use inference rules

Development
===========

### Tests

.. code-block:: shell

    # Install test dependencies
    $ pip install -e .[test]

    # Run tests
    $ py.test

    # Skip slow tests
    $ py.test -m 'not slow'

    # Run tests with coverage
    $ py.test --cov=bemserver --cov-report term-missing


Running the application
=======================

### Settings environment variables


.. code-block:: shell

    FLASK_ENV=development  # development or production
    FLASK_SETTINGS_FILE=  # path to optional settings path

Since bemserver uses python-dotenv, you may store them in an .env file at the root of the application.


### Launch core api server


From the activated BEMServer virtual environment, once the environment variables are set.

.. code-block:: shell

    # Run API
    $ flask run


Managing the SQL database
=========================

The database is versionned with Flask-Migrate (http://flask-migrate.readthedocs.io/).

While developing, when the model changes, Flask-Migrate can help creating
migration scripts by comparing the model in the code to a database in a state
corresponding to the former revision. It can also apply thoses scripts to
another database instance.

### Creating a migration script

Set environment variables (see above). Then,

.. code-block:: shell

    # Create migration script
    $ flask db migrate --message 'Useful message' --rev-id optional_rev_id

The sripts are written in the "migrations" directory. They should be reviewed
carefully, as Alembic (use internally by Flask-Migrate) has shortcomings.
For instance, it has issues with custom types such as UUID.

### Create or upgrade an existing database

SQLALCHEMY_DATABASE_URI points to the DB file. The directory should be writable by www-data.

The db file should be created automatically. If not, try to to create an empty DB file using `touch`:

.. code-block:: shell

    $ touch event.db
    $ chown www-data:www-data event.db
    $ chmod 600 sqlite.db

You may want to shut down the application during the process.

Finally, use flask CLI to create/upgrade the DB.

Set environment variables (see above). Then,

.. code-block:: shell

    # Migrate the base
    $ flask db upgrade


Managing API authentication
===========================

API authentication can be activated by setting AUTHENTICATION_ENABLED flask config variable to True.
3 authentication methods are available:
  - JSON Web Token (using AUTH_JWT_ENABLED), for anonymous occupants (to fill occupants survey)
  - by certificate (using AUTH_CERTIFICATE_ENABLED), for machine users (application modules)
  - SAML (using AUTH_SAML_ENABLED), for human users using Hit2Gap portal, not implemented yet

Each authentication method has its specific endpoint and parameters.
More information is available in API documentation.

### Certificate authentication

We use caman (https://github.com/radiac/caman) as self-signatory Certificate Authority manager.
With this tool we deliver an authentication certificate to clients (application modules).
