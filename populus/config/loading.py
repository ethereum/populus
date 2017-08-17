import anyconfig

from .helpers import (
    get_global_default_json_config_file_path,
)

from .glob import (
    GlobalConfig,
)


def load_config(config_file_path):
    config = anyconfig.load(config_file_path)
    return config

def load_global_config(global_config_path=None):

    if global_config_path is None:
        global_config_path = get_global_default_json_config_file_path()

    config = load_config(global_config_path)
    return GlobalConfig(config)


def write_config(project_dir, config, write_path):
    with open(write_path, 'w') as config_file:
        anyconfig.dump(
            dict(config),
            config_file,
            sort_keys=True,
            indent=2,
            separators=(',', ': '),
        )

    return write_path
