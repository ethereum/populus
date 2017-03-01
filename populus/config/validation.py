import os

import jsonschema

import anyconfig

from eth_utils import (
    to_tuple,
)

from populus import ASSETS_DIR


CONFIG_SCHEMA_FILENAMES = {
    '1': "config.v1.schema.json",
    '2': "config.v2.schema.json",
}
LATEST_VERSION = '2'


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
def validate_config(config, version=LATEST_VERSION):
    schema = load_config_schema(version)
    validator = jsonschema.Draft4Validator(schema)
    for error in validator.iter_errors(config):
        yield error
