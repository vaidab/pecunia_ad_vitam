import os
from functools import wraps
from getpass import getpass
from time import time, sleep

import config
from package import encryption


def timeit(func):
    """
    :param func: Decorated function
    :return: Execution time for the decorated function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        print(f"[d] {func.__name__}() executed in {int(end - start)} seconds")
        # print(f"[+] {func.__name__}() executed in {end - start:.4f} seconds")
        return result

    return wrapper


def debug(func):
    """Print the function signature and return value"""

    @wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]  # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)  # 3
        print(f"[d] Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"[d] {func.__name__!r} returned {value!r}")  # 4
        return value

    return wrapper_debug


def slow_down(_func=None, *, rate=1):
    """Sleep given amount of seconds before calling the function"""

    def decorator_slow_down(func):
        @wraps(func)
        def wrapper_slow_down(*args, **kwargs):
            sleep(rate)
            return func(*args, **kwargs)

        return wrapper_slow_down

    if _func is None:
        return decorator_slow_down
    else:
        return decorator_slow_down(_func)


def get_private_key():
    if os.getenv('PRIVATE_KEY'):
        return os.getenv('PRIVATE_KEY')
    elif config.private_key:
        return encryption.decrypt_private_key(config.private_key)
    else:
        return getpass(prompt="[+] Input private key: ")



