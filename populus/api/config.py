from populus.config.glob import (
    GlobalConfig,
)

from populus.config.helpers import (
    get_global_default_json_config_file_path,
)

from populus.config.loading import (
    load_config,
)

def load_global_config(global_config_path=None):

    if global_config_path is None:
        global_config_path = get_global_default_json_config_file_path()

    config = load_config(global_config_path)
    return GlobalConfig(config)

