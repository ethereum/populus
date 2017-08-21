import os

import jsonschema

import anyconfig

from eth_utils import (
    to_tuple,
)

from populus import ASSETS_DIR
from populus.defaults import (
    PROJECT_JSON_CONFIG_SCHEMA,
    USER_JSON_CONFIG_SCHEMA,
)
from .versions import (
    V1,
    V2,
    V3,
    V4,
    V5,
    LATEST_VERSION,
)


CONFIG_SCHEMA_FILENAMES = {
    V1: "config.v1.schema.json",
    V2: "config.v2.schema.json",
    V3: "config.v3.schema.json",
    V4: "config.v4.schema.json",
    V5: "config.v5.schema.json",
}


assert LATEST_VERSION in CONFIG_SCHEMA_FILENAMES


def get_user_config_schema_path():

    return os.path.join(ASSETS_DIR, USER_JSON_CONFIG_SCHEMA)


def load_user_config_schema():
    config_schema_path = get_user_config_schema_path()
    config_schema = anyconfig.load(config_schema_path)
    return config_schema


def get_project_config_schema_path():

    return os.path.join(ASSETS_DIR, PROJECT_JSON_CONFIG_SCHEMA)


def load_project_config_schema():
    config_schema_path = get_project_config_schema_path()
    config_schema = anyconfig.load(config_schema_path)
    return config_schema


@to_tuple
def get_validation_errors(config, schema):
    validator = jsonschema.Draft4Validator(schema)
    for error in validator.iter_errors(dict(config)):
        yield error


def validate_config(config, schema):
    errors = get_validation_errors(config, schema)
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