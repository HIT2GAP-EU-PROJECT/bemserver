"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from os import path
from setuptools import setup, find_packages


# Get the long description from the README file
_SETUP_PATH = path.abspath(path.dirname(__file__))
with open(path.join(_SETUP_PATH, 'README.md'), encoding='utf-8') as f:
    _LONG_DESCRIPTION = f.read()


setup(
    name='bemserver',
    version='0.0.1',
    description='BEMServer API',
    long_description=_LONG_DESCRIPTION,
    url='https://bemserver.org',
    # Author details
    author='Nobatek/INEF4',
    author_email='contact@bemserver.org',
    license='GNU Affero General Public License',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    # What does your project relate to?
    keywords='building energy management api',
    packages=find_packages(exclude=['tests*']),

    package_data={
        '': ['database/timeseries/*.csv'],
    },
    install_requires=[
        'Werkzeug>=0.16.0,<0.17.0',
        'flask>=1.1.0,<1.2.0',
        'flask_marshmallow>=0.7.0',
        'flask-rest-api>=0.10.0,<0.11.0',
        'webargs>=5.1.3,<6.0',
        'apispec>=0.39.0,<1.0.0',
        'python-dateutil>=2.5.0,<2.9.0',
        'marshmallow>=2.15.2,<3.0.0',
        'marshmallow-oneofschema>=1.0.5,<2.0.0',
        'requests>=2.22.0,<2.23.0',
        'numpy>=1.14.0,<1.18.0',
        'pandas>=0.25.0,<0.26.0',
        'sparqlwrapper>=1.8.4,<1.9.0',
        'flask-jwt-simple>=0.0.3,<0.1.0',
        'python3-saml>=1.4.1,<1.5',
        'tables>=3.3.0,<3.6.0',
        'pint>0.7,<0.9',
        'sqlalchemy>=1.2.5,<1.4.0',
        'sqlalchemy-utils>=0.32.21,<0.35.0',
        'flask-sqlalchemy>=2.3.2,<2.5.0',
        'flask-migrate>=2.1.1,<2.6.0',
        'python-dotenv>=0.8.2,<0.11.0',
        'pytz==2019.2',
    ],
)
