Deployment
==========

See main README first.

This file provides additional information for deployment on production servers.

### Web server

Install apache, WSGI plugin and activate ssl

.. code-block:: shell

    $ aptitude install apache2 libapache2-mod-wsgi-py3
    $ a2enmod ssl

Create a new site in /etc/apache2/sites-available using bemserver.conf
as an example.
bemserver-ssl.conf includes certificate authentication rules.

### Application installation and configuration

As unprivileged user:

- Clone or pull the code repository
- Checkout the right commit

As root:

- Create or activate virtualenv
- Install application

Copy settings.cfg and customize configuration.

Copy application.wsgi and let it point to settings.cfg.

apache2 site configuration file above should point to this application.wsgi.

### Logging

Create logfiles directory with appropriate permissions and pass its path
as configuration parameter.

### Data storages

If needed, create storage directories for data (HDF5 files, IFC file...) with
appropriate permissions and pass their paths as configuration parameters.

For instance:

.. code-block:: shell

    $ mkdir /path_to_storage_dir/hdf5
    $ chmod 770 /path_to_storage_dir/hdf5
    $ chgrp www-data /path_to_storage_dir/hdf5

#### HDF5 files repack

HDF5 files tend to grow huge pretty quickly. Directory repack_hdf5/ contains
scripts that can be used to repack them on a regulare basis.

Copy those scripts somewhere, adapt the paths, set a cron task and you're good
to go.

.. code-block:: shell

    # Launch every Sunday at noon
    0 12 * * 0 /path_to_/bemserver/repack_hdf5.sh

### Authentication

#### SAML

Default setting files (settings.json and advanced_settings.json) can be found at https://github.com/onelogin/python3-saml#settings

Update (set <sp_domain>, <idp_domain> and <idp_cert>) and copy saml/settings.json and saml/advanced_settings.json to AUTH_SAML_DIR path.

### Launch application

Activate site in apache and reload configuration:

.. code-block:: shell

    $ a2ensite bemserver
    $ systemctl reload apache2
