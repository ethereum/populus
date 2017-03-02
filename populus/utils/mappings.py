import operator
import itertools

from eth_utils import (
    is_dict,
    to_dict,
    compose,
    to_tuple,
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


@to_tuple
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
        if is_dict(value):
            for sub_key, sub_value in flatten_mapping(value, prefix):
                yield sub_key, sub_value
        else:
            yield '.'.join(prefix), value


@to_dict
def deep_merge_dicts(*dicts):
    for key in set(itertools.chain(*(_dict.keys() for _dict in dicts))):
        values = tuple((_dict[key] for _dict in dicts if key in _dict))
        if is_dict(values[-1]):
            yield key, deep_merge_dicts(*(
                _dict[key]
                for _dict
                in dicts
                if is_dict(_dict.get(key))
            ))
        else:
            yield key, values[-1]
