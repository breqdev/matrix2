from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar
from datadog.dogstatsd.base import statsd

T = TypeVar("T")
P = ParamSpec("P")


def timed(image: str):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            t0 = time.time()
            result = func(*args, **kwargs)
            statsd.gauge(
                "matrix.load_seconds",
                time.time() - t0,
                tags=[f"image:{image}"],
            )
            return result

        return wrapper

    return decorator
