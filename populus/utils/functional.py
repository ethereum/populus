import functools
import itertools

from .string import (
    normalize_class_name,
)


class cached_property(object):
    """
    Source: Django (django.utils.functional)

    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    Optional ``name`` argument allows you to make cached properties of other
    methods. (e.g.  url = cached_property(get_absolute_url, name='url') )
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


def noop(*args, **kwargs):
    pass


def to_object(class_name, bases=None):
    if bases is None:
        bases = (object,)

    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            props = fn(*args, **kwargs)
            return type(normalize_class_name(class_name), bases, props)
        return inner
    return outer


def apply_to_return_value(callback):
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            return callback(fn(*args, **kwargs))

        return inner
    return outer


chain_return = apply_to_return_value(itertools.chain.from_iterable)
