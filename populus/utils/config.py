import os
import operator
import itertools

import anyconfig

from populus import ASSETS_DIR

from .types import (
    is_string,
    is_object,
)
from .module_loading import (
    import_string,
)
from .functional import (
    compose,
    cast_return_to_tuple,
    sort_return,
)


CONFIG_SCHEMA_FILENAME = "config.schema.json"


def get_config_schema_path():
    return os.path.join(ASSETS_DIR, CONFIG_SCHEMA_FILENAME)


JSON_CONFIG_FILENAME = './populus.json'


def get_json_config_file_path(project_dir=None):
    if project_dir is None:
        project_dir = os.getcwd()

    json_config_file_path = os.path.join(project_dir, JSON_CONFIG_FILENAME)
    return json_config_file_path


def check_if_json_config_file_exists(project_dir=None):
    if project_dir is None:
        project_dir = os.getcwd()

    json_config_file_path = get_json_config_file_path(project_dir)
    return os.path.exists(json_config_file_path)


get_default_project_config_file_path = get_json_config_file_path


def get_empty_config():
    empty_config = anyconfig.to_container({})
    return empty_config


@cast_return_to_tuple
@sort_return
def flatten_config_items(config, base_prefix=None):
    """
    An `.items()` implementation for nested configuration dictionaries.  It
    flattens out the entire keyspace returning an interable of 2-tuples.

    >>> flatten_config_items({'a': {'b': {'c': 1}, 'd': 2}, 'e': 3})
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
            for sub_key, sub_value in flatten_config_items(value, prefix):
                yield sub_key, sub_value
        else:
            yield '.'.join(prefix), value


def resolve_config(config, master_config):
    if '$ref' in config:
        if len(config.keys()) != 1:
            raise KeyError(
                "Config references may not contain extra keys.  The keys "
                "'{0}' were found.".format("', '".join(config.keys()))
            )
        if not has_nested_key(master_config, config['$ref']):
            raise KeyError(
                "Config reference {0} is not present in master configuration".format(
                    config['$ref'],
                )
            )
        return get_nested_key(master_config, config['$ref'])
    else:
        return config


def set_nested_key(config, key, value):
    key_head, _, key_tail = key.rpartition('.')

    head_setters = (
        operator.methodcaller('setdefault', key_part, get_empty_config())
        for key_part
        in key_head.split('.')
        if key_part
    )
    tail_setter = operator.methodcaller('__setitem__', key_tail, value)

    setter_fn = compose(*itertools.chain(head_setters, (tail_setter,)))

    # must write to both the config_for_read and config_for_write
    return setter_fn(config)


class empty(object):
    pass


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


class ClassImportPath(object):
    def __init__(self, key):
        self.key = key

    def __get__(self, obj, type=None):
        class_import_path = obj[self.key]
        klass = import_string(class_import_path)
        return klass

    def __set__(self, obj, value):
        if is_string(value):
            obj[self.key] = value
        elif isinstance(value, type):
            obj[self.key] = '.'.join([value.__module__, value.__name__])
        else:
            raise ValueError(
                "Unsupported type.  Must be either a string import path or a "
                "chain class"
            )
