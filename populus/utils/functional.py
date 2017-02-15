import itertools
import collections

from eth_utils import (
    to_dict,
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


@to_dict
def deep_merge_dicts(*dicts):
    for key in set(itertools.chain(*(_dict.keys() for _dict in dicts))):
        values = tuple((_dict[key] for _dict in dicts if key in _dict))
        if isinstance(values[-1], collections.Mapping):
            yield key, deep_merge_dicts(*(
                _dict[key]
                for _dict
                in dicts
                if isinstance(_dict.get(key), collections.Mapping)
            ))
        else:
            yield key, values[-1]


def noop(*args, **kwargs):
    pass
