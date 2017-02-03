import os

import anyconfig

from populus import ASSETS_DIR

from .types import (
    is_string,
)
from .mappings import (
    get_nested_key,
    has_nested_key,
)
from .module_loading import (
    import_string,
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
