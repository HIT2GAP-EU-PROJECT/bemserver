"""Hateoas stuff

using flask-marshmallow:
https://github.com/marshmallow-code/flask-marshmallow
"""

import warnings

# https://github.com/marshmallow-code/flask-marshmallow/issues/53
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from flask_marshmallow import Marshmallow


ma_hateoas = Marshmallow()
