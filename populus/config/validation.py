import os

import jsonschema

import anyconfig

from eth_utils import (
    to_tuple,
)

from populus import ASSETS_DIR

from .versions import (
    V1,
    V2,
    V3,
    LATEST_VERSION
)

CONFIG_SCHEMA_FILENAMES = {
    V1: "config.v1.schema.json",
    V2: "config.v2.schema.json",
    V3: "config.v3.schema.json",
}


assert LATEST_VERSION in CONFIG_SCHEMA_FILENAMES


def get_config_schema_path(version=LATEST_VERSION):
    try:
        return os.path.join(ASSETS_DIR, CONFIG_SCHEMA_FILENAMES[version])
    except KeyError:
        raise KeyError(
            "`version` must be one of {0}".format(
                sorted(tuple(CONFIG_SCHEMA_FILENAMES.keys()))
            )
        )


def load_config_schema(version=LATEST_VERSION):
    config_schema_path = get_config_schema_path(version)
    config_schema = anyconfig.load(config_schema_path)
    return config_schema


@to_tuple
def get_validation_errors(config, version=None):
    if version is None and 'version' in config:
        version = config['version']
    elif version is None:
        version = LATEST_VERSION
    schema = load_config_schema(version)
    validator = jsonschema.Draft4Validator(schema)
    for error in validator.iter_errors(dict(config)):
        yield error


def validate_config(config, version=None):
    errors = get_validation_errors(config, version)
    if errors:
        error_message = format_errors(errors)
        raise ValueError(error_message)


def format_errors(errors):
    return '\n'.join((
        '\n--------------------{e.path}-----------------\n{e.message}\n'.format(
            e=error,
        )
        for error in errors
    ))
