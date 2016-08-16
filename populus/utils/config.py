import os
import copy
import itertools

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from .chains import (
    get_default_ipc_path,
)


CONFIG_SEARCH_PATHS = [
    os.path.expanduser('~'),
]

PRIMARY_CONFIG_FILENAME = 'populus.ini'
CONFIG_FILENAMES = [
    PRIMARY_CONFIG_FILENAME,
]


TESTRPC_DEFAULTS = {
    'provider': 'web3.providers.rpc.TestRPCProvider',
}

MAINNET_DEFAULTS = {
    'provider': 'web3.providers.ipc.IPCProvider',
    'ipc_path': get_default_ipc_path(testnet=False),
}

MORDEN_DEFAULTS = {
    'provider': 'web3.providers.ipc.IPCProvider',
    'ipc_path': get_default_ipc_path(testnet=True),
}


class Config(configparser.ConfigParser):
    @property
    def chains(self):
        defaults = {
            'mainnet': copy.deepcopy(MAINNET_DEFAULTS),
            'morden': copy.deepcopy(MORDEN_DEFAULTS),
            'testrpc': copy.deepcopy(TESTRPC_DEFAULTS),
        }
        declared_chains = {
            section.partition(':')[2]: {
                section_key: self.get(section, section_key)
                for section_key in self.options(section)
            }
            for section in self.sections()
            if section.startswith('chain:')
        }
        defaults.update(declared_chains)
        return defaults


def get_config_paths(project_dir, extra_paths=CONFIG_SEARCH_PATHS):
    search_paths = [project_dir] + extra_paths
    all_config_file_paths = [
        os.path.join(path, filename)
        for path, filename
        in itertools.product(search_paths, CONFIG_FILENAMES)
    ]
    return all_config_file_paths


def load_config(config_file_paths):
    config = Config()
    config.read(reversed(config_file_paths))

    return config
