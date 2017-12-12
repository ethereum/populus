import anyconfig

from populus import ASSETS_DIR
from populus.utils.filesystem import (
    is_under_path,
)


def load_config(config_file_path):
    config = anyconfig.load(config_file_path)
    return config


def write_config(config, write_path):
    if is_under_path(ASSETS_DIR, write_path):
        raise Exception("Invariant: Should not be writing to populus assets path")

    with open(write_path, 'w') as config_file:
        anyconfig.dump(
            dict(config),
            config_file,
            sort_keys=True,
            indent=2,
            separators=(',', ': '),
        )

    return write_path
