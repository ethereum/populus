import os
import copy

import anyconfig

from populus import ASSETS_DIR

from populus.utils.functional import (
    cast_return_to_tuple,
)
from populus.utils.chains import (
    get_default_ipc_path as get_geth_default_ipc_path,
)
from populus.utils.config import (
    get_nested_key,
    has_nested_key,
    set_nested_key,
    pop_nested_key,
    get_empty_config,
    flatten_config_items,
    get_ini_config_file_path,
    resolve_config,
)


class empty(object):
    pass


class Config(object):
    parent = None
    default_config_info = None
    config_for_read = None
    config_for_write = None

    def __init__(self, config=None, default_config_info=None, parent=None):
        if config is None:
            config = get_empty_config()
        elif isinstance(config, dict):
            config = anyconfig.to_container(config)

        if default_config_info is None:
            default_config_info = tuple()
        self.default_config_info = default_config_info
        self.config_for_write = config
        self.config_for_read = apply_default_configs(
            self.config_for_write,
            self.default_config_info,
        )
        self.parent = parent

    def get_master_config(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_master_config()

    def resolve(self, value):
        if isinstance(value, dict):
            return resolve_config(value, self.get_master_config())
        else:
            return value

    def get(self, key, default=None):
        try:
            return get_nested_key(self.config_for_read, key)
        except KeyError:
            return default

    def get_config(self, key, defaults=None):
        try:
            return type(self)(self.resolve(self[key]), defaults, parent=self)
        except KeyError:
            return type(self)(get_empty_config(), defaults, parent=self)

    def pop(self, key, default=empty):
        try:
            value = pop_nested_key(self.config_for_read, key)
        except KeyError:
            if default is empty:
                raise
            else:
                value = default

        try:
            pop_nested_key(self.config_for_write, key)
        except KeyError:
            pass

        return value

    def setdefault(self, key, value):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value

    @cast_return_to_tuple
    def keys(self, flatten=False):
        for key, _ in self.items(flatten=flatten):
            yield key

    @cast_return_to_tuple
    def items(self, flatten=False):
        if flatten:
            _items = flatten_config_items(self.config_for_read)
        else:
            _items = self.config_for_read.items()
        for key, value in _items:
            yield key, value

    def update(self, other, **kwargs):
        if isinstance(other, type(self)):
            self.config_for_read.update(copy.deepcopy(other.config_for_read), **kwargs)
            self.config_for_write.update(copy.deepcopy(other.config_for_write), **kwargs)
        else:
            self.config_for_read.update(copy.deepcopy(other), **kwargs)
            self.config_for_write.update(copy.deepcopy(other), **kwargs)

    def __str__(self):
        return str(self.config_for_read)

    def __repr__(self):
        return repr(self.config_for_read)

    def __eq__(self, other):
        return self.config_for_read == other

    def __bool__(self):
        if self.config_for_write:
            return True
        elif not self.default_config_info:
            return False
        else:
            return any(tuple(zip(*self.default_config_info)[1]))

    def __nonzero__(self):
        return self.__bool__()

    def __len__(self):
        return len(self.config_for_read)

    def __getitem__(self, key):
        return get_nested_key(self.config_for_read, key)

    def __setitem__(self, key, value):
        if isinstance(value, type(self)):
            set_nested_key(self.config_for_read, key, value.config_for_read)
            return set_nested_key(self.config_for_write, key, value.config_for_write)
        else:
            set_nested_key(self.config_for_read, key, value)
            return set_nested_key(self.config_for_write, key, value)

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __iter__(self):
        return iter(self.keys())

    def __copy__(self):
        return type(self)(
            copy.copy(self.config_for_write),
            copy.copy(self.default_config_info),
        )

    def __deepcopy__(self, memo):
        return type(self)(
            copy.deepcopy(self.config_for_write, memo),
            copy.deepcopy(self.default_config_info, memo),
        )


def set_geth_mainnet_ipc_path(config):
    set_nested_key(
        config,
        'provider.settings.ipc_path',
        get_geth_default_ipc_path(testnet=False),
    )
    return config


def set_geth_ropsten_ipc_path(config):
    set_nested_key(
        config,
        'provider.settings.ipc_path',
        get_geth_default_ipc_path(testnet=True),
    )
    return config


POPULUS_CONFIG_DEFAULTS = {
    #
    # Chains
    #
    # Temp Geth Chains
    ('chains.temp.web3',),
    # Mainnet
    ('chains.mainnet.web3',),
    # Ropsten
    ('chains.ropsten.web3',),
    # TestRPC
    ('chains.testrpc.web3',),
    # Tester
    ('chains.tester.web3',),
    #
    # Web3 Presets
    #
    ('web3.InfuraRopsten',),
    ('web3.InfuraMainnet',),
    (
        'web3.GethMainnet',
        'web3.GethMainnet.config.json',
        anyconfig.MS_NO_REPLACE,
        set_geth_mainnet_ipc_path,
    ),
    (
        'web3.GethRopsten',
        'web3.GethRopsten.config.json',
        anyconfig.MS_NO_REPLACE,
        set_geth_ropsten_ipc_path,
    ),
    ('web3.GethEphemeral',),
    ('web3.TestRPC',),
    ('web3.Tester',),
}


@cast_return_to_tuple
def load_default_config_info(config_defaults=POPULUS_CONFIG_DEFAULTS):
    for config_value in config_defaults:
        if len(config_value) == 1:
            write_path = config_value[0]
            config_file_name = "{0}.config.json".format(write_path)
            merge_strategy = anyconfig.MS_NO_REPLACE
            callback = None
        elif len(config_value) == 2:
            write_path, config_file_name = config_value
            merge_strategy = anyconfig.MS_NO_REPLACE
            callback = None
        elif len(config_value) == 3:
            write_path, config_file_name, merge_strategy = config_value
            callback = None
        elif len(config_value) == 4:
            write_path, config_file_name, merge_strategy, callback = config_value
        else:
            raise ValueError("Invalid Default Configuration")

        config_file_path = os.path.join(ASSETS_DIR, config_file_name)
        loaded_config = anyconfig.load(config_file_path)

        if callback is not None:
            processed_config = callback(loaded_config)
        else:
            processed_config = loaded_config

        yield write_path, processed_config, merge_strategy


def apply_default_configs(config, default_configs):
    merged_config = copy.deepcopy(config)

    for write_path, default_config, merge_strategy in default_configs:
        if has_nested_key(merged_config, write_path):
            sub_config = copy.deepcopy(get_nested_key(merged_config, write_path))
            sub_config_with_merge_rules = anyconfig.to_container(
                sub_config,
                ac_merge=merge_strategy,
            )
            sub_config_with_merge_rules.update(default_config)

            set_nested_key(merged_config, write_path, sub_config_with_merge_rules)
        else:
            set_nested_key(merged_config, write_path, default_config)

    return merged_config


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
