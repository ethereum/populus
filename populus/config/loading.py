import anyconfig

from populus.utils.config import (
    get_config_schema_path,
)


def load_config(config_file_path):
    config = anyconfig.load(config_file_path)
    return config


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


def load_config_schema():
    config_schema_path = get_config_schema_path()
    config_schema = anyconfig.load(config_schema_path)
    return config_schema
