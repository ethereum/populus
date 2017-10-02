import anyconfig


def load_config(config_file_path):
    config = anyconfig.load(config_file_path)
    return config


def write_config(config, write_path):
    with open(write_path, 'w') as config_file:
        anyconfig.dump(
            dict(config),
            config_file,
            sort_keys=True,
            indent=2,
            separators=(',', ': '),
        )

    return write_path
