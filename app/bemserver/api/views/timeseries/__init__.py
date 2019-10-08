"""Api timeseries module initialization"""

from ...extensions.rest_api import rest_api, Blueprint


DESCRIPTION = """Operations on timeseries

Those endpoints allow to get, set and delete timeseries values.

Resampling
----------

Asking for data on a large time interval can involve important amounts of data and lead to timeouts.

Data can be downsampled on the fly if high-frequency precision is not needed. For instance, it is possible to query monthly averages over a year.

Unit conversion
---------------

Unit conversion can also be done on the fly. When specifying a unit while getting data, the API returns data converted to that unit. Conversely, when setting data, it is possible to send it in another unit, provided the unit is passed along with the query, and the API will take care of converting it to the storage unit. Of course, unit conversion is only possible for unit combinations that make sense, like Celcius/Fahrenheit or meter/kilometer.

The units used internally are defined in the `pint` Python library. The list is available [online](https://github.com/hgrecco/pint/blob/master/pint/default_en.txt). For convenience, we added the `'percent'`, `'permille'` and `'ppm'` units.

If a data is stored as 'percent' in the database (e.g. 42%), it is possible to get it in normal form (0.42) by querying `'dimensionless'` unit.

Providing units that don't match or even invalid units will result in a 422 (invalid input) error.

Aggregation
-----------

Aggregation consist in performing basic arithmetic operation on mumtiple time series so as to get a unique output timeseries. Some scenario could be:

- compute the general energy consumption in a building as the sum of values from different meters;

- compute the average temperature in a room based on the temperature measured by different sensors in this room...

"""

bp = Blueprint('timeseries', __name__, url_prefix='/timeseries',
               description=DESCRIPTION)


def init_app(app):
    """Initialize application with module"""

    from . import views  # noqa

    rest_api.register_blueprint(bp)
