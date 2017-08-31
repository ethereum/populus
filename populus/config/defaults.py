import os
import json

from populus import ASSETS_DIR
from populus.defaults import (
    PROJECT_JSON_CONFIG_DEFAULTS,
)


def get_default_project_config_path():

    return os.path.join(ASSETS_DIR, PROJECT_JSON_CONFIG_DEFAULTS)


def load_default_project_config():
    default_config_path = get_default_project_config_path()
    with open(default_config_path) as default_config_file:
        default_config = json.load(default_config_file)
    return default_config
