import collections
import operator
import os

import anyconfig

from eth_utils import (
    compose,
    is_string,
    to_ordered_dict,
)

from populus import ASSETS_DIR
from populus.config.loading import (
    load_config,
)
from populus.config.versions import (
    V1,
    V2,
    V3,
    V4,
    V5,
    V6,
    V7,
    V8,
    LATEST_VERSION,
    KNOWN_LEGACY_VERSIONS,
    LAST_LEGACY_CONFIG_VERSION,
)
from populus.utils.mappings import (
    get_nested_key,
    has_nested_key,
)
from populus.utils.module_loading import (
    import_string,
)

LEGACY_CONFIG_FILENAME = './populus.json'

PROJECT_CONFIG_FILENAME = './project.json'

POPULUS_CONFIG_FILENAME = './config.json'
DEFAULT_POPULUS_DIR = '~/.populus'

DEFAULT_V1_CONFIG_FILENAME = "defaults.v1.config.json"
DEFAULT_V2_CONFIG_FILENAME = "defaults.v2.config.json"
DEFAULT_V3_CONFIG_FILENAME = "defaults.v3.config.json"
DEFAULT_V4_CONFIG_FILENAME = "defaults.v4.config.json"
DEFAULT_V5_CONFIG_FILENAME = "defaults.v5.config.json"
DEFAULT_V6_CONFIG_FILENAME = "defaults.v6.config.json"
DEFAULT_V7_CONFIG_FILENAME = "defaults.v7.config.json"
DEFAULT_V8_CONFIG_FILENAME = "config.project.defaults.v8.json"

DEFAULT_POPULUS_V7_CONFIG_FILENAME = "defaults.populus.v7.config.json"
DEFAULT_POPULUS_V8_CONFIG_FILENAME = "config.populus.defaults.v8.json"


LEGACY_DEFAULT_CONFIG_FILENAMES = {
    V1: DEFAULT_V1_CONFIG_FILENAME,
    V2: DEFAULT_V2_CONFIG_FILENAME,
    V3: DEFAULT_V3_CONFIG_FILENAME,
    V4: DEFAULT_V4_CONFIG_FILENAME,
    V5: DEFAULT_V5_CONFIG_FILENAME,
}

DEFAULT_CONFIG_FILENAMES = {
    V6: DEFAULT_V6_CONFIG_FILENAME,
    V7: DEFAULT_V7_CONFIG_FILENAME,
    V8: DEFAULT_V8_CONFIG_FILENAME,
}

DEFAULT_POPULUS_CONFIG_FILENAMES = {
    V8: DEFAULT_POPULUS_V8_CONFIG_FILENAME,
}


#
# Populus level config utils
#
def get_default_populus_config_path(version=LATEST_VERSION):

    try:
        return os.path.join(ASSETS_DIR, DEFAULT_POPULUS_CONFIG_FILENAMES[version])
    except KeyError:
        raise KeyError(
            "`version` must be one of {0}".format(
                sorted(tuple(DEFAULT_POPULUS_CONFIG_FILENAMES.keys()))
            )
        )


def load_default_populus_config(version=LATEST_VERSION):
    default_config_path = get_default_populus_config_path(version)
    default_config = load_config(default_config_path)
    return default_config


def get_populus_config_file_path():
    return os.path.expanduser(os.path.join(
        os.environ.get(
            'POPULUS_DIR',
            DEFAULT_POPULUS_DIR,
        ),
        POPULUS_CONFIG_FILENAME
    ))


def check_if_populus_config_file_exists():
    populus_config_file_path = get_populus_config_file_path()
    return os.path.exists(populus_config_file_path)


#
# Project level config utils
#
def get_default_project_config_path(version=LATEST_VERSION):
    try:
        return os.path.join(ASSETS_DIR, DEFAULT_CONFIG_FILENAMES[version])
    except KeyError:
        raise KeyError(
            "`version` must be one of {0}".format(
                sorted(tuple(DEFAULT_CONFIG_FILENAMES.keys()))
            )
        )


def load_default_project_config(version=LATEST_VERSION):
    default_config_path = get_default_project_config_path(version)
    default_config = load_config(default_config_path)
    return default_config


def get_project_config_file_path(project_dir):
    project_config_file_path = os.path.join(project_dir, PROJECT_CONFIG_FILENAME)
    return project_config_file_path


def check_if_project_config_file_exists(project_dir):
    project_config_file_path = get_project_config_file_path(project_dir)
    return os.path.exists(project_config_file_path)


#
# LEGACY config utils
#
def get_default_legacy_config_path(version):
    if version not in KNOWN_LEGACY_VERSIONS:
        raise ValueError(
            "The requested version v{0} is not part of the legacy config "
            "versions.  The last legacy version was v{1}".format(
                version,
                LAST_LEGACY_CONFIG_VERSION,
            )
        )
    return os.path.join(ASSETS_DIR, DEFAULT_CONFIG_FILENAMES[version])


def load_default_legacy_config(version):
    default_config_path = get_default_legacy_config_path(version)
    default_config = load_config(default_config_path)
    return default_config


def get_legacy_config_file_path(project_dir):
    legacy_config_file_path = os.path.join(project_dir, LEGACY_CONFIG_FILENAME)
    return legacy_config_file_path


def check_if_legacy_config_file_exists(project_dir):
    legacy_config_file_path = get_legacy_config_file_path(project_dir)
    return os.path.exists(legacy_config_file_path)


def get_empty_config():
    if hasattr(anyconfig, 'to_container'):
        empty_config = anyconfig.to_container({})
    else:
        empty_config = {}
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


@to_ordered_dict
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
