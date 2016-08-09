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


def get_config_search_paths(project_dir, extra_paths=CONFIG_SEARCH_PATHS):
    return tuple(itertools.product(CONFIG_SEARCH_PATHS, CONFIG_FILENAMES))


def load_config(search_paths):
    all_possible_config_paths = [
        os.path.join(path, filename)
        for path, filename
        in itertools.product(search_paths, CONFIG_FILENAMES)
        if os.path.exists(os.path.join(path, filename))
    ]
    config = configparser.ConfigParser()
    config.read(reversed(all_possible_config_paths))

    return config
