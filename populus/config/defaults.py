import os
import json

from populus import ASSETS_DIR

from .versions import (
    V1,
    V2,
    V3,
    V4,
    V5,
    LATEST_VERSION
)


DEFAULT_V1_CONFIG_FILENAME = "defaults.v1.config.json"
DEFAULT_V2_CONFIG_FILENAME = "defaults.v2.config.json"
DEFAULT_V3_CONFIG_FILENAME = "defaults.v3.config.json"
DEFAULT_V4_CONFIG_FILENAME = "defaults.v4.config.json"
DEFAULT_V5_CONFIG_FILENAME = "defaults.v5.config.json"


DEFAULT_CONFIG_FILENAMES = {
    V1: DEFAULT_V1_CONFIG_FILENAME,
    V2: DEFAULT_V2_CONFIG_FILENAME,
    V3: DEFAULT_V3_CONFIG_FILENAME,
    V4: DEFAULT_V4_CONFIG_FILENAME,
    V5: DEFAULT_V5_CONFIG_FILENAME,
}


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
