from collections.abc import Callable
from functools import wraps
from time import time
from typing import ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


def ttl_cache(seconds: int):
    """Cache function result for `seconds` time period"""

    def get_ttl_hash():
        """Return the same value within `seconds` time period"""
        return round(time() / seconds)

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        h = get_ttl_hash()

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal h
            if h != get_ttl_hash() or not hasattr(wrapper, "value"):
                h = get_ttl_hash()
                wrapper.value = func(*args, **kwargs)
            return wrapper.value  # type: ignore

        return wrapper

    return decorator
