import anyconfig

from populus.utils.config import (
    get_ini_config_file_path,
)


def load_config(config_file_path):
    config = anyconfig.load(config_file_path)
    return config


def write_config(project_dir, config, write_path):
    if write_path == get_ini_config_file_path(project_dir):
        raise ValueError(
            "The INI configuration format has been deprecated.  Please convert "
            "your configuration file to either `populus.yml` or `populus.json`"
        )

    with open(write_path, 'w') as config_file:
        anyconfig.dump(
            config,
            config_file,
            sort_keys=True,
            indent=2,
            separators=(',', ': '),
        )

    return write_path
