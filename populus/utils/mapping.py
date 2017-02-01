import operator
import itertools

from .functional import (
    compose,
)


def set_nested_key(config, key, value):
    key_head, _, key_tail = key.rpartition('.')

    head_setters = (
        operator.methodcaller('setdefault', key_part, dict())
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
