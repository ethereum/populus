import os
import json

from populus import ASSETS_DIR

from .versions import (
    V1,
    V2,
    V3,
    V4,
    V5,
    V6,
    V7,
    V8,
    V9,
    LATEST_VERSION
)


DEFAULT_V1_CONFIG_FILENAME = "defaults.v1.config.json"
DEFAULT_V2_CONFIG_FILENAME = "defaults.v2.config.json"
DEFAULT_V3_CONFIG_FILENAME = "defaults.v3.config.json"
DEFAULT_V4_CONFIG_FILENAME = "defaults.v4.config.json"
DEFAULT_V5_CONFIG_FILENAME = "defaults.v5.config.json"
DEFAULT_V6_CONFIG_FILENAME = "defaults.v6.config.json"
DEFAULT_V7_CONFIG_FILENAME = "defaults.v7.config.json"
DEFAULT_V8_CONFIG_FILENAME = "defaults.v8.config.json"
DEFAULT_V9_CONFIG_FILENAME = "defaults.v9.config.json"

DEFAULT_USER_V7_CONFIG_FILENAME = "defaults.user.v7.config.json"
DEFAULT_USER_V8_CONFIG_FILENAME = "defaults.user.v8.config.json"
DEFAULT_USER_V9_CONFIG_FILENAME = "defaults.user.v9.config.json"


DEFAULT_CONFIG_FILENAMES = {
    V1: DEFAULT_V1_CONFIG_FILENAME,
    V2: DEFAULT_V2_CONFIG_FILENAME,
    V3: DEFAULT_V3_CONFIG_FILENAME,
    V4: DEFAULT_V4_CONFIG_FILENAME,
    V5: DEFAULT_V5_CONFIG_FILENAME,
    V6: DEFAULT_V6_CONFIG_FILENAME,
    V7: DEFAULT_V7_CONFIG_FILENAME,
    V8: DEFAULT_V8_CONFIG_FILENAME,
    V9: DEFAULT_V9_CONFIG_FILENAME,
}

DEFAULT_USER_CONFIG_FILENAMES = {
    V7: DEFAULT_USER_V7_CONFIG_FILENAME,
    V8: DEFAULT_USER_V8_CONFIG_FILENAME,
    V9: DEFAULT_USER_V9_CONFIG_FILENAME,
}


def get_user_default_config_path(version=LATEST_VERSION):

    try:
        return os.path.join(ASSETS_DIR, DEFAULT_USER_CONFIG_FILENAMES[version])
    except KeyError:
        raise KeyError(
            "`version` must be one of {0}".format(
                sorted(tuple(DEFAULT_USER_CONFIG_FILENAMES.keys()))
            )
        )


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


def load_user_default_config(version=LATEST_VERSION):
    default_config_path = get_user_default_config_path(version)
    with open(default_config_path) as default_config_file:
        default_config = json.load(default_config_file)
    return default_config
