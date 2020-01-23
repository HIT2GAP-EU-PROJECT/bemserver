## Installation


BEMServer is built upon different tools and use various libraries. The main dependencies are:

- the use of [SQLite](https://www.sqlite.org/index.html) to store events
- the use of [Apache Jena Fuseki](https://jena.apache.org/index.html) to store the BEMOnt data model

Additionally, one may need to secure the APIs. Three modes have been used and tested:

- JSON web token
- credentials using SAML
- certificates generated with caman

Finally, an IFC extractor has been developed so as to populate the data model from an IFC file. This tool uses the IfcOpenShell library.


### Install core

```bash
# In application folder
cd bemserver/app/

# Update package list
apt-get update

# Install required packages, python header files and development stuff
# (libxmlsec1-dev is required by python3-saml)
apt-get install g++ make libxmlsec1-dev pkg-config
apt-get install python3-dev python3-venv

# Create virtual environment
python3 -m venv $YOUR_VIRTUALENV_DIR/bemserver

# Activate virtual environment
source $YOUR_VIRTUALENV_DIR/bemserver/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install
pip install -r requirements.txt

```


### Install IfcOpenShell

IfcOpenShell has to be installed manually. The IfcOpenShell-python archive can be found in the [official website](http://ifcopenshell.org/python).

**Version >="0.5.0 preview 2" is required.**


```bash
# In a temporary folder
cd /tmp

# Download IfcOpenShell-python archive
wget https://github.com/IfcOpenShell/IfcOpenShell/releases/download/v0.5.0-preview2/ifcopenshell-python35-master-9ad68db-linux64.zip

# Unzip archive
unzip ifcopenshell-python35-master-9ad68db-linux64.zip

# Place ifcopenshell in the python environment's site-packages folder
mv ifcopenshell $YOUR_VIRTUALENV_DIR/bemserver/lib/python3.5/site-packages/
```


### Install Apache Jena Fuseki

Apache Jena Fuseki is required to store the BEMOnt model. A preconfigured docker image is distributed to ease Apache Jena Fuseki configuration with Bemserver:  https://hub.docker.com/r/nbkinef4/bemserver-fuseki

```bash
# Create a fuseki container
docker run -d --name fuseki -p 3030:3030 \
	-v fuseki-data:/fuseki \
	-e ADMIN_PASSWORD=pickasupersecurepassword \
    -e JVM_ARGS=-Xmx2048M \
    --log-opt max-size=10m --log-opt max-file=3 \
    --restart unless-stopped \
    nbkinef4/bemserver-fuseki

# On subsequent runs, just use
docker restart fuseki

```

#### Web interface

You can manage ontology browsing: http://localhost:3030/

#### Configuration files

- `/fuseki/shiro.ini` - *Beware this file should be modified when deploying the solution at the production level to ensure a safer access to the dataset.*

- `/fuseki/configuration/bemserver_tdb.ttl` - *Beware bemserver_tdb.ttl creates a persistent dataset called 'bemserver'. See the [Jena documentation](https://jena.apache.org/documentation/) for more information on how to configure your dataset.*

#### More info

- [Apache Jena official website](https://jena.apache.org/index.html)
- [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/index.html)
- [Docker documentation](https://docs.docker.com/)
- [Docker installation on Debian](https://docs.docker.com/install/linux/docker-ce/debian/)


<!--#### TODO: describe configuration to use inference rules-->



## Development


### Tests

```bash
# In application folder
cd bemserver/app/

# Install test dependencies
pip install -r dev-requirements.txt

# Run tests
py.test

# Skip slow tests
py.test -m 'not slow'

# Run tests with coverage
py.test --cov=bemserver --cov-report term-missing
```



## Running the application


### Settings environment variables

```bash
FLASK_ENV=development  # development or production
FLASK_SETTINGS_FILE=  # path to optional settings path
```

Since bemserver uses python-dotenv, you may store them in an .env file at the root of the application folder (`app`).


### Launch core api server

From the activated BEMServer virtual environment, once the environment variables are set.

```bash
# Run API
flask run --host=0.0.0.0 --port=8080
```



## Managing the SQL database


The database is versionned with Flask-Migrate (http://flask-migrate.readthedocs.io/).

While developing, when the model changes, Flask-Migrate can help creating
migration scripts by comparing the model in the code to a database in a state
corresponding to the former revision. It can also apply thoses scripts to
another database instance.


### Creating a migration script

Set environment variables (see above). Then,


```bash
# Create migration script
flask db migrate --message 'Useful message' --rev-id optional_rev_id
```

The sripts are written in the "migrations" directory. They should be reviewed
carefully, as Alembic (use internally by Flask-Migrate) has shortcomings.
For instance, it has issues with custom types such as UUID.


### Create or upgrade an existing database

SQLALCHEMY_DATABASE_URI points to the DB file. The directory should be writable by www-data.

The db file should be created automatically. If not, try to to create an empty DB file using `touch`:

```bash
touch event.db
chown www-data:www-data event.db
chmod 600 sqlite.db
```

You may want to shut down the application during the process.

Finally, use flask CLI to create/upgrade the DB.

Set environment variables (see above). Then,

```bash
# Migrate the base
flask db upgrade
```



## Managing API authentication


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
