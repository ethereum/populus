import os
import collections
import operator

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
    cast_return_to_ordered_dict,
)
from .mapping import (
    has_nested_key,
    get_nested_key,
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


@cast_return_to_ordered_dict
def sort_prioritized_configs(backend_configs, master_config):
    resolved_backend_configs = tuple(
        (
            backend_name,
            resolve_config(backend_configs.get_config(backend_name), master_config),
        )
        for backend_name
        in backend_configs
    )
    backends_with_conflicting_priorities = tuple((
        backend_name
        for backend_name, count
        in collections.Counter((
            (backend_name, config['priority'])
            for backend_name, config
            in resolved_backend_configs
        )).items()
        if count > 1
    ))
    if backends_with_conflicting_priorities:
        raise ValueError(
            "The following package backends have conflicting priority "
            "values.  '{0}'.  Ensure that all priority values are unique "
            "across all backends.".format(
                ', '.join((backends_with_conflicting_priorities))
            )
        )

    return sorted(
        resolved_backend_configs,
        key=compose(*(
            operator.itemgetter(1),
            operator.itemgetter('priority'),
        )),
    )
