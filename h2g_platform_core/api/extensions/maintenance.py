"""Maintenance mode"""

from flask_rest_api import abort


HTTP_METHODS = (
    'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'TRACE')


def init_app(app):
    """Put the app in maintenance mode

    Set a catch-all route to return a 503 on any request

    Inspired by http://flask.pocoo.org/snippets/57/
    """
    @app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
    @app.route('/<path:path>', methods=HTTP_METHODS)
    def maintenance_mode_error(path):
        abort(503)
