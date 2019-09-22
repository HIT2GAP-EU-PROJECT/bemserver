"""Concurrency requests limiter

Inspired by Flask-Limiter
"""

from collections import defaultdict
from threading import BoundedSemaphore
from functools import wraps

from flask import request
from werkzeug.exceptions import TooManyRequests


# From flask-limiter
def get_remote_address():
    """Get IP address for the current request (or 127.0.0.1 if none found)

    This won't work behind a proxy. See flask-limiter docs.
    """
    return request.remote_addr or '127.0.0.1'


class NonBlockingBoundedSemaphore(BoundedSemaphore):
    def __enter__(self):
        ret = self.acquire(blocking=False)
        if ret is False:
            raise TooManyRequests(
                'Only {} concurrent request(s) allowed'
                .format(self._initial_value))
        return ret


class ConcurrencyLimiter:

    def __init__(self, app=None, key_func=get_remote_address):
        self.app = app
        self.key_func = key_func
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['concurrency_limiter'] = {
            'semaphores': defaultdict(dict),
        }

    def limit(self, max_concurrent_requests=1):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Limiter not initialized
                if self.app is None:
                    return func(*args, **kwargs)
                identity = self.key_func()
                sema = self.app.extensions['concurrency_limiter'][
                    'semaphores'][func].setdefault(
                        identity,
                        NonBlockingBoundedSemaphore(max_concurrent_requests)
                    )
                with sema:
                    return func(*args, **kwargs)
            return wrapper
        return decorator


limiter = ConcurrencyLimiter()


def init_app(app):
    """Initialize limiter"""

    limiter.init_app(app)
    if app.config['AUTHENTICATION_ENABLED']:
        from bemserver.api.extensions.auth import get_identity

        def get_uid():
            return get_identity()['uid']

        limiter.key_func = get_uid
