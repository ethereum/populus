import operator
import itertools

from .types import (
    is_object,
)
from .functional import (
    compose,
    cast_return_to_tuple,
    sort_return,
)


def set_nested_key(config, key, value, mapping_type=dict):
    key_head, _, key_tail = key.rpartition('.')

    head_setters = (
        operator.methodcaller('setdefault', key_part, mapping_type())
        for key_part
        in key_head.split('.')
        if key_part
    )
    tail_setter = operator.methodcaller('__setitem__', key_tail, value)

    setter_fn = compose(*itertools.chain(head_setters, (tail_setter,)))

    # must write to both the config_for_read and config_for_write
    return setter_fn(config)


def get_nested_key(config, key):
    key_head, _, key_tail = key.rpartition('.')

    head_getters = (
        operator.itemgetter(key_part)
        for key_part
        in key_head.split('.')
        if key_part
    )

    tail_getter = operator.itemgetter(key_tail)

    getter_fn = compose(*itertools.chain(head_getters, (tail_getter,)))

    return getter_fn(config)


def delete_nested_key(config, key):
    key_head, _, key_tail = key.rpartition('.')

    head_getters = (
        operator.itemgetter(key_part)
        for key_part
        in key_head.split('.')
        if key_part
    )
    tail_deleter = operator.methodcaller('__delitem__', key_tail)

    del_fn = compose(*itertools.chain(head_getters, (tail_deleter,)))

    return del_fn(config)


def has_nested_key(config, key):
    try:
        get_nested_key(config, key)
    except KeyError:
        return False
    else:
        return True


def pop_nested_key(config, key):
    key_head, _, key_tail = key.rpartition('.')

    head_getters = (
        operator.itemgetter(key_part)
        for key_part
        in key_head.split('.')
        if key_part
    )
    tail_popper = operator.methodcaller('pop', key_tail)

    popper_fn = compose(*itertools.chain(head_getters, (tail_popper,)))

    return popper_fn(config)


@cast_return_to_tuple
@sort_return
def flatten_mapping(config, base_prefix=None):
    """
    An `.items()` implementation for nested configuration dictionaries.  It
    flattens out the entire keyspace returning an interable of 2-tuples.

    >>> flatten_mapping({'a': {'b': {'c': 1}, 'd': 2}, 'e': 3})
    (
        ('a.b.c', 1),
        ('a.d', 2),
        ('e': 3),
    )
    """
    if base_prefix is None:
        base_prefix = tuple()

    for key, value in config.items():
        prefix = base_prefix + (key,)
        if is_object(value):
            for sub_key, sub_value in flatten_mapping(value, prefix):
                yield sub_key, sub_value
        else:
            yield '.'.join(prefix), value
