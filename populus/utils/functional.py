import functools
import collections


def noop(*args, **kwargs):
    pass


def identity(value):
    return value


def combine(f, g):
    return lambda x: f(g(x))


def compose(*functions):
    return functools.reduce(combine, reversed(functions), identity)


def apply_formatters_to_return(*formatters):
    formatter = compose(*formatters)

    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            value = fn(*args, **kwargs)
            return formatter(value)
        return inner
    return outer


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


def cast_return(_type):
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            return _type(fn(*args, **kwargs))

        return inner
    return outer


cast_return_to_tuple = cast_return(tuple)
cast_return_to_list = cast_return(list)
cast_return_to_dict = cast_return(dict)
sort_return = cast_return(sorted)
cast_return_to_ordered_dict = cast_return(collections.OrderedDict)
