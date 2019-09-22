"""Debugging tools"""

import time
import datetime as dt
import enum


def time_this(func):
    """Decorator to get a function's execution time (printed in console output).
    """
    def wrapper(*args, **kwargs):
        t_start_exec = time.perf_counter()
        ret = func(*args, **kwargs)
        t_elapsed_exec = time.perf_counter() - t_start_exec
        printable_args = get_printable_args(*args, **kwargs)
        print('TIME [{}.{}({})]: {} (seconds)'.format(
            args[0].__class__.__name__ if len(args) > 0 else '?',
            func.__name__, printable_args, t_elapsed_exec))
        return ret
    return wrapper


def get_printable_args(*args, **kwargs):
    """Stringify args and kwargs to a printable format.

    :returns str: Printable args/kwargs string.
    """
    primitive_types = (int, float, complex, str, bool, enum.Enum, dt.datetime)
    printable_args = [
        str(arg) if isinstance(arg, primitive_types) else str(type(arg))
        for arg in args]
    printable_args.extend([
        '{}={}'.format(k, v) for k, v in sorted(kwargs.items())])
    return ', '.join(printable_args)
