import os
import json

from populus import ASSETS_DIR


DEFAULT_V1_CONFIG_FILENAME = "defaults.v1.config.json"
DEFAULT_V2_CONFIG_FILENAME = "defaults.v2.config.json"


DEFAULT_CONFIG_FILENAMES = {
    '1': DEFAULT_V1_CONFIG_FILENAME,
    '2': DEFAULT_V2_CONFIG_FILENAME,
}
LATEST_VERSION = '2'


assert LATEST_VERSION in DEFAULT_CONFIG_FILENAMES


def get_default_config_path(version=LATEST_VERSION):
    try:
        return os.path.join(ASSETS_DIR, DEFAULT_CONFIG_FILENAMES[version])
    except KeyError:
        raise KeyError(
            "`version` must be one of {0}".format(
                sorted(tuple(DEFAULT_CONFIG_FILENAMES.keys()))
            )
        )


def load_default_config(version=LATEST_VERSION):
    default_config_path = get_default_config_path(version)
    with open(default_config_path) as default_config_file:
        default_config = json.load(default_config_file)
    return default_config
