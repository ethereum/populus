import os
import itertools
import configparser


CONFIG_SEARCH_PATHS = [
    os.path.expanduser('~'),
]

CONFIG_FILENAMES = [
    'populus.ini',
]


"""
[populus]
project_dir=/a-path/
"""


def get_config_paths(project_dir, extra_paths=CONFIG_SEARCH_PATHS):
    search_paths = [project_dir] + extra_paths
    all_config_file_paths = [
        os.path.join(path, filename)
        for path, filename
        in itertools.product(search_paths, CONFIG_FILENAMES)
    ]
    return all_config_file_paths


def load_config(config_file_paths):
    config = configparser.ConfigParser()
    config.read(reversed(config_file_paths))

    return config


class Config(object):
    def __init__(self, overrides,
