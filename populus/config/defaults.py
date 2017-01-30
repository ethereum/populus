import os
import json

from populus import ASSETS_DIR


DEFAULT_CONFIG_FILENAME = "defaults.config.json"


def get_default_config_path():
    return os.path.join(ASSETS_DIR, DEFAULT_CONFIG_FILENAME)


def load_default_config():
    default_config_path = get_default_config_path()
    with open(default_config_path) as default_config_file:
        default_config = json.load(default_config_file)
    return default_config
